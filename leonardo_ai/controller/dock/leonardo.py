import time
import requests
from typing import Callable

from PyQt5 import QtCore
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QByteArray, QThread

from krita import DockWidget, Node, Document, Selection

from .ui_sketch2image import Sketch2Image
from ...client.abstract import JobStatus, AbstractClient, Generation
from ...client.graphql.graphql import GraphqlClient
from ...client.restClient import RestClient
from ...view.dock import Ui_LeonardoAI
from ...config import Config, ConfigRegistry
from ...util.thread import Thread


class BalanceUpdater(QThread):

  def __init__(self, leonardoClient: Callable[[], AbstractClient], ui: Ui_LeonardoAI):
    super().__init__()

    self.getLeonardoAI = leonardoClient
    self.ui = ui

  def run(self):
    leonardoAI = self.getLeonardoAI()
    if leonardoAI is not None:
      self.ui.lcdBalance.display(str(leonardoAI.getUserInfo().Token.General))

class LeonardoDock(Sketch2Image):
  generationThread: Thread = None
  sigGenerationDone = QtCore.pyqtSignal()
  sigGenerationFailed = QtCore.pyqtSignal(Exception)
  sigGenerationDoneText2Image = QtCore.pyqtSignal(Generation)
  sigGenerationDoneInpaint = QtCore.pyqtSignal(Generation)
  sigGenerationDoneOutpaint = QtCore.pyqtSignal(Generation)
  sigGenerationDoneImage2Image = QtCore.pyqtSignal(Generation)
  sigGenerationDoneSketch2Image = QtCore.pyqtSignal(Generation)

  def __init__(self):
    super().__init__()
    self.config = Config.instance()

    self.sigGenerationDone.connect(self.onGenerationDone)
    self.sigGenerationFailed.connect(self.onGenerationFailed)
    self.sigGenerationDoneText2Image.connect(self.onGenerationDoneText2Image)
    self.sigGenerationDoneInpaint.connect(self.onGenerationDoneInpaint)
    self.sigGenerationDoneOutpaint.connect(self.onGenerationDoneOutpaint)
    self.sigGenerationDoneImage2Image.connect(self.onGenerationDoneImage2Image)
    self.sigGenerationDoneSketch2Image.connect(self.onGenerationDoneSketch2Image)

    self.modelLoadingThread = None
    self._initialiseSDK()

    def getLeonardoAI(): return self.leonardoAI
    self.balanceUpdater = BalanceUpdater(getLeonardoAI, self.ui)
    self.updateBalance()

  def _initialiseSDK(self):
    clientType = self.config.get(ConfigRegistry.LEONARDO_CLIENT_TYPE)
    if clientType == "gql":
      self.leonardoAI = GraphqlClient(
        self.config.get(ConfigRegistry.LEONARDO_CLIENT_GQL_USERNAME),
        self.config.get(ConfigRegistry.LEONARDO_CLIENT_GQL_PASSWORD),
      )
    elif clientType == "rest":
      self.leonardoAI = RestClient(self.config.get(ConfigRegistry.LEONARDO_CLIENT_REST_KEY))
    else:
      self.leonardoAI = None

    if self.modelLoadingThread is not None:
      return

    def loadModels(t):
      models = self.leonardoAI.getModels(favorites=True)
      for model in models: self.sigAddModel.emit(model)

      models = self.leonardoAI.getModels(official=True)
      for model in models: self.sigAddModel.emit(model)

    self.modelLoadingThread = Thread(loadModels)
    self.modelLoadingThread.start()

  def canvasChanged(self, canvas):
    pass

  def onSettingsChanged(self):
    super().onSettingsChanged()
    self._initialiseSDK()
    self.updateBalance()


  def updateBalance(self):
    if self.balanceUpdater.isRunning() and not self.balanceUpdater.isFinished(): return
    self.balanceUpdater.start()

  def onGenerate(self):
    super().onGenerate()

    if self.ui.cmbMode.currentIndex() == 0: self.onImage()
    if self.ui.cmbMode.currentIndex() == 1: self.onInpaint()
    if self.ui.cmbMode.currentIndex() == 2: self.onOutpaint()
    if self.ui.cmbMode.currentIndex() == 3: self.onImage2Image()
    if self.ui.cmbMode.currentIndex() == 4: self.onSketch2Image()

  def onInterrupt(self):
    super().onInterrupt()

    if self.generationThread is not None:
      self.generationThread.requestInterruption()

  def generate(self, genFunc: Callable[[...], str], genArgs: dict, signal: QtCore.pyqtBoundSignal):
    self.ui.btnGenerate.setEnabled(False)

    if self.generationThread is not None and self.generationThread.isRunning():
      self.generationThread.terminate()

    def run(t: QThread):
      try:
        genId = genFunc(**genArgs)
      except Exception as e:
        self.sigGenerationDone.emit()
        self.sigGenerationFailed.emit(e)
        return

      while not t.isInterruptionRequested():
        time.sleep(1)
        job = self.leonardoAI.getGenerationById(genId)

        if job.Status == JobStatus.COMPLETE:
          signal.emit(job)
          break
        if job.Status == JobStatus.FAILED:
          self.sigGenerationFailed.emit(Exception(f"""Job failed: {job.Id}"""))
          break

      self.sigGenerationDone.emit()
      self.updateBalance()

    self.generationThread = Thread(run)
    self.generationThread.start()

  @QtCore.pyqtSlot()
  def onGenerationDone(self):
    self.ui.btnGenerate.setEnabled(True)
    self.ui.btnGenerate.setVisible(True)
    self.ui.btnInterrupt.setVisible(False)

  def loadGeneratedImages(self, generation: Generation, document, selection = None):
    grpLayer = document.createGroupLayer(f"""AI - {generation.Prompt} - {generation.Id}""")
    document.rootNode().addChildNode(grpLayer, None)
    for generatedImage in generation.GeneratedImages:
      image = QImage.fromData(requests.get(generatedImage.Url).content)
      layer = document.createNode(generatedImage.Id, "paintlayer")
      grpLayer.addChildNode(layer, None)

      ptr = image.bits()
      ptr.setsize(image.byteCount())
      layer.setPixelData(
        QByteArray(ptr.asstring()),
        0 if selection is None else selection.x(),
        0 if selection is None else selection.y(),
        image.width(),
        image.height(),
      )

      if selection is not None:
        layer.cropNode(selection.x(), selection.y(), selection.width(), selection.height())

        invertedSelection = selection.duplicate()
        invertedSelection.invert()
        invertedSelection.cut(layer)

  def onImage(self):
    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSaveForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
      "width": self.dimWidth, "height": self.dimHeight,
      "tiling": self.t2iTiling,
    }
    if self.ui.grpAdvancedSettings.isVisible():
      args.update({
        "guidanceScale": self.guidanceScale, "seed": self.seed, "scheduler": self.scheduler, "inferenceSteps": self.stepCount,
      })
    if self.ui.chkPhotoReal.isChecked():
      args.update({
        "photoRealStrength": self.photoRealStrength, "photoRealHighContrast": not self.photoRealRawMode, "photoRealStyle": self.photoRealStyle,
      })
    if self.ui.chkAlchemy.isChecked():
      args.update({
        "alchemyHighResolution": self.alchemyHighResolution, "alchemyContrastBoost": self.alchemyContrastBoost, "alchemyResonance": self.alchemyResonance,
        "promptMagicVersion": self.alchemyPromptMagicVersion, "promptMagicStrength": self.alchemyPromptMagicStrength, "promptMagicHighContrast": self.alchemyHighContrast,
      })

    self.generate(self.leonardoAI.createImageGeneration, args, self.sigGenerationDoneText2Image)

  @QtCore.pyqtSlot(Generation)
  def onGenerationFailed(self, error: Exception):
    print("Generation failed!", error)

  @QtCore.pyqtSlot(Generation)
  def onGenerationDoneText2Image(self, generation: Generation):
    document = Krita.instance().activeDocument()
    self.loadGeneratedImages(generation, document)

    document.crop(0, 0, max(document.width(), generation.ImageWidth), max(document.height(), generation.ImageHeight))
    document.refreshProjection()

  def onInpaint(self):
    document = Krita.instance().activeDocument()
    selection = document.selection()

    img = self.partFromSelection(document, selection)
    mask = self.maskFromSelection(selection)

    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSaveForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
      "imageStrength": 1.0 - self.inpaintStrength,
      "image": img, "mask": mask,
    }
    if self.ui.grpAdvancedSettings.isVisible():
      args.update({
        "guidanceScale": self.guidanceScale, "seed": self.seed, "scheduler": self.scheduler, "inferenceSteps": self.stepCount,
      })

    self.generate(self.leonardoAI.createInpaintGeneration, args, self.sigGenerationDoneInpaint)

  @QtCore.pyqtSlot(Generation)
  def onGenerationDoneInpaint(self, generation: Generation):
    document = Krita.instance().activeDocument()
    selection = document.selection()
    self.loadGeneratedImages(generation, document, selection)

    document.refreshProjection()

  def onOutpaint(self):
    document = Krita.instance().activeDocument()
    selection = document.selection()

    img = self.partFromSelection(document, selection)

    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSaveForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
      "imageStrength": 0.1,
      "image": img
    }
    if self.ui.grpAdvancedSettings.isVisible():
      args.update({
        "guidanceScale": self.guidanceScale, "seed": self.seed, "scheduler": self.scheduler, "inferenceSteps": self.stepCount,
      })

    self.generate(self.leonardoAI.createInpaintGeneration, args, self.sigGenerationDoneOutpaint)

  @QtCore.pyqtSlot(Generation)
  def onGenerationDoneOutpaint(self, generation: Generation):
    document = Krita.instance().activeDocument()
    selection = document.selection()
    self.loadGeneratedImages(generation, document, selection)

    document.refreshProjection()
    document.crop(
      min(selection.x(), 0),
      min(selection.y(), 0),
      max(selection.x() + selection.width(), document.width() + abs(min(selection.x(), 0))),
      max(selection.y() + selection.height(), document.height() + abs(min(selection.y(), 0))),
    )

  def onImage2Image(self):
    document = Krita.instance().activeDocument()
    selection = document.selection()

    img = self.partFromSelection(document, selection)

    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSaveForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
      "image": img,
      "imageStrength": self.imageStrength, "tiling": self.tiling,
    }
    if self.ui.grpAdvancedSettings.isVisible():
      args.update({
        "guidanceScale": self.guidanceScale, "seed": self.seed, "scheduler": self.scheduler, "inferenceSteps": self.stepCount,
      })
    if self.controlNet:
      args.update({
        "poseToImage": self.controlNetType,
        "controlnetWeight": self.controlNetWeight,
      })
    if self.ui.chkI2IAlchemy.isChecked():
      args.update({
        "alchemyHighResolution": self.alchemyI2IHighResolution, "alchemyContrastBoost": self.alchemyI2IContrastBoost, "alchemyResonance": self.alchemyI2IResonance,
      })

    self.generate(self.leonardoAI.createImage2ImageGeneration, args, self.sigGenerationDoneImage2Image)

  @QtCore.pyqtSlot(Generation)
  def onGenerationDoneImage2Image(self, generation: Generation):
    document = Krita.instance().activeDocument()
    selection = document.selection()
    self.loadGeneratedImages(generation, document, selection)

    document.refreshProjection()

  def onSketch2Image(self):
    document = Krita.instance().activeDocument()
    selection = document.selection()

    img = self.partFromSelection(document, selection)
    mask = self.maskFromSelection(selection)

    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSaveForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
      "image": img, "mask": mask,
    }
    if self.ui.chkOverrideDefaults.isChecked():
      args.update({
        "imageStrength": self.inputStrength
      })
    if self.ui.grpAdvancedSettings.isVisible():
      args.update({
        "guidanceScale": self.guidanceScale, "seed": self.seed, "scheduler": self.scheduler, "inferenceSteps": self.stepCount,
      })

    self.generate(self.leonardoAI.createSketch2ImageGeneration, args, self.sigGenerationDoneImage2Image)

  @QtCore.pyqtSlot(Generation)
  def onGenerationDoneSketch2Image(self, generation: Generation):
    document = Krita.instance().activeDocument()
    selection = document.selection()
    self.loadGeneratedImages(generation, document, selection)

    document.refreshProjection()

  def maskFromSelection(self, selection: Selection | None = None) -> QImage:
    selection = selection if selection is not None else Krita.instance().activeDocument().selection()

    width = max(selection.width(), 512)
    height = max(selection.height(), 512)
    return QImage(
      selection.pixelData(selection.x(), selection.y(), width, height),
      width,
      height,
      width,
      QImage.Format_Grayscale8,
    )

  def partFromSelection(self,
                        document: Document | None = None,
                        selection: Selection | None = None) -> QImage:

    document = document if document is not None else Krita.instance().activeDocument()
    selection = selection if selection is not None else document.selection()

    width = max(selection.width(), 512)
    height = max(selection.height(), 512)
    return QImage(
      document.pixelData(selection.x(), selection.y(), width, height),
      width,
      height,
      QImage.Format_ARGB32,
    )