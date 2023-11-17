from typing import Callable
from PyQt5 import QtCore
from PyQt5.QtCore import QByteArray, QObject
from PyQt5.QtGui import QImage, QPixmap
from krita import Document, Selection

from .threads import imageThread
from ..client.abstract import Generation, Image

class GenerationLoader(QObject):
  sigImageLoaded = QtCore.pyqtSignal(QPixmap, Image)

  def __init__(self,
               document: Document,
               selection: Selection,
               generation: Generation,
               afterLoad: Callable[[Document, Selection], None] | None = None,
               selectedImages: dict[int, bool] | None = None):
    super().__init__()

    self.document = document
    self.selection = selection
    self.generation = generation
    self.selectedImages = selectedImages
    self.images = {}

    self.grpLayer = self.document.createGroupLayer(f"""AI - {self.generation.Prompt} - {self.generation.Id}""")
    self.document.rootNode().addChildNode(self.grpLayer, None)

    self.afterLoad = afterLoad if afterLoad is not None else self._doNothing
    self.sigImageLoaded.connect(self._onImageLoaded)

  def _doNothing(self, document: Document, selection: Selection):
    pass

  def load(self):
    self.imageLoaded = 0
    self.imageToLoad = sum(value for value in self.selectedImages.values() if value)

    # load image in own thread
    for i, generatedImage in enumerate(self.generation.GeneratedImages):
      # skip images which should not be loaded
      if self.selectedImages is not None and i in self.selectedImages and not self.selectedImages[i]: continue

      il = imageThread(generatedImage.Url, self.sigImageLoaded, metaData=generatedImage)
      il.start()

  @QtCore.pyqtSlot(QPixmap, Image)
  def _onImageLoaded(self, data: QPixmap, image: Image):
    self.imageLoaded += 1

    layer = self.document.createNode(image.Id, "paintlayer")
    image = QImage(data)
    self.grpLayer.addChildNode(layer, None)

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

    # check if we are done
    if self.imageLoaded == self.imageToLoad:
      # call callback
      self.afterLoad(self.document, self.selection)

      self.document.refreshProjection()
