import requests
from typing import Callable
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QByteArray
from PyQt5.QtGui import QImage
from krita import Document, Selection
from ..client.abstract import Generation, Image

class imageLoader(QThread):
  def __init__(self, image: Image):
    super().__init__()

    self.image = image
    self.qimage = None

  def run(self):
    self.qimage = QImage.fromData(requests.get(self.image.Url).content)

class GenerationLoader(QThread):
  sigDone = QtCore.pyqtSignal()

  def __init__(self,
               document: Document,
               selection: Selection,
               generation: Generation,
               afterLoad: Callable[[Document, Selection], None] | None = None):
    super().__init__()

    self.document = document
    self.selection = selection
    self.generation = generation
    self.images = {}

    self.afterLoad = afterLoad if afterLoad is not None else self._doNothing
    self.sigDone.connect(self._onDone)

  def _doNothing(self, document: Document, selection: Selection):
    pass

  def run(self):
    imgLoader = []

    # load image in own thread
    for generatedImage in self.generation.GeneratedImages:
      il = imageLoader(generatedImage)
      imgLoader.append(il)
      il.start()

    # wait for all images to load
    for il in imgLoader:
      il.wait()
      self.images.update({ il.image.Id: il.qimage })

    self.sigDone.emit()

  @QtCore.pyqtSlot()
  def _onDone(self):
    grpLayer = self.document.createGroupLayer(f"""AI - {self.generation.Prompt} - {self.generation.Id}""")
    self.document.rootNode().addChildNode(grpLayer, None)

    for generatedImage in self.generation.GeneratedImages:
      image = self.images[generatedImage.Id]
      layer = self.document.createNode(generatedImage.Id, "paintlayer")
      grpLayer.addChildNode(layer, None)

      ptr = image.bits()
      ptr.setsize(image.byteCount())
      layer.setPixelData(
        QByteArray(ptr.asstring()),
        0 if self.selection is None else self.selection.x(),
        0 if self.selection is None else self.selection.y(),
        image.width(),
        image.height(),
      )

      if self.selection is not None:
        layer.cropNode(self.selection.x(), self.selection.y(), self.selection.width(), self.selection.height())

        invertedSelection = self.selection.duplicate()
        invertedSelection.invert()
        invertedSelection.cut(layer)

    # call callback
    self.afterLoad(self.document, self.selection)

    self.document.refreshProjection()