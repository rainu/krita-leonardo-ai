import time
from typing import Callable

from PyQt5 import QtCore
from PyQt5.QtGui import QImage

from krita import DockWidget, Node, Document, Selection, GroupLayer

from .ui_sketch2image import Sketch2Image
from ...client.abstract import JobStatus, Generation, TokenBalance
from ...client.graphql.graphql import GraphqlClient
from ...client.restClient import RestClient
from ...config import Config, ConfigRegistry
from ...util.threads import GeneralThread
from ...util.generationLoader import GenerationLoader


class LeonardoDock(Sketch2Image):
  generationThread: GeneralThread = None
  balanceUpdaterThread: GeneralThread = None

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
    self.generationLoadingThread = None
    self._initialiseSDK()

    if self.leonardoAI is None:
      self.ui.btnSettings.click()

    self.updateBalance()

  def getLeonardoAI(self):
    return self.leonardoAI

  def _getBalance(self, q: GeneralThread) -> TokenBalance:
    return self.getLeonardoAI().getUserInfo().Token

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

    if self.leonardoAI is None or self.modelLoadingThread is not None:
      return

    def loadModels(t):
      models = self.leonardoAI.getModels(favorites=True)
      for model in models: self.sigAddModel.emit(model)

      models = self.leonardoAI.getModels(official=True)
      for model in models: self.sigAddModel.emit(model)

    self.modelLoadingThread = GeneralThread(loadModels)
    self.modelLoadingThread.start()

  def canvasChanged(self, canvas):
    pass

  def onSettingsChanged(self):
    super().onSettingsChanged()
    self._initialiseSDK()
    self.updateBalance()


  def updateBalance(self):
    if self.balanceUpdaterThread is not None and self.balanceUpdaterThread.isRunning(): return

    self.balanceUpdaterThread = GeneralThread(self._getBalance, self.sigBalanceUpdate)
    self.balanceUpdaterThread.start()

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

  def onLoadGeneration(self, generation: Generation, selectedImages: dict[int, bool] | None):
    super().onLoadGeneration(generation, selectedImages)

    self.onGenerationDoneText2Image(generation, selectedImages)

  def generate(self, genFunc: Callable[[...], str], genArgs: dict, signal: QtCore.pyqtBoundSignal):
    self.ui.btnGenerate.setEnabled(False)

    if self.generationThread is not None and self.generationThread.isRunning():
      self.generationThread.terminate()

    def run(t: GeneralThread):
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

    self.generationThread = GeneralThread(run)
    self.generationThread.start()

  @QtCore.pyqtSlot()
  def onGenerationDone(self):
    self.ui.btnGenerate.setEnabled(True)
    self.ui.btnGenerate.setVisible(True)
    self.ui.btnInterrupt.setVisible(False)

  def onImage(self):
    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSafeForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
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
  def onGenerationDoneText2Image(self, generation: Generation, selectedImages: dict[int, bool] | None = None):
    def afterLoad(document: Document, selection: Selection):
      document.crop(0, 0, max(document.width(), generation.ImageWidth), max(document.height(), generation.ImageHeight))

    self.generationLoadingThread = GenerationLoader(Krita.instance().activeDocument(),None, generation, afterLoad, selectedImages)
    self.generationLoadingThread.load()

  def onInpaint(self):
    document = Krita.instance().activeDocument()
    selection = document.selection()

    img = self.partFromSelection(document, selection)
    mask = self.maskFromSelection(selection)

    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSafeForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
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
    self.generationLoadingThread = GenerationLoader(document, selection, generation)
    self.generationLoadingThread.load()

  def onOutpaint(self):
    document = Krita.instance().activeDocument()
    selection = document.selection()

    img = self.partFromSelection(document, selection)

    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSafeForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
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
    def afterLoad(document: Document, selection: Selection):
      document.crop(
        min(selection.x(), 0),
        min(selection.y(), 0),
        max(selection.x() + selection.width(), document.width() + abs(min(selection.x(), 0))),
        max(selection.y() + selection.height(), document.height() + abs(min(selection.y(), 0))),
      )

    document = Krita.instance().activeDocument()
    selection = document.selection()
    self.generationLoadingThread = GenerationLoader(document, selection, generation, afterLoad)
    self.generationLoadingThread.load()

  def onImage2Image(self):
    document = Krita.instance().activeDocument()
    selection = document.selection()

    img = self.partFromSelection(document, selection)

    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSafeForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
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
    self.generationLoadingThread = GenerationLoader(document, selection, generation)
    self.generationLoadingThread.load()

  def onSketch2Image(self):
    document = Krita.instance().activeDocument()
    selection = document.selection()

    img = self.partFromSelection(document, selection)
    mask = self.maskFromSelection(selection)

    args = {
      "modelId": self.model.Id, "sdVersion": self.model.StableDiffusionVersion, "presetStyle": self.presetStyle,
      "prompt": self.prompt, "negativePrompt": self.negativePrompt,
      "notSafeForWork": self.nsfw, "public": self.public, "numberOfImages": self.numberOfImages,
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
    self.generationLoadingThread = GenerationLoader(document, selection, generation)
    self.generationLoadingThread.load()

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