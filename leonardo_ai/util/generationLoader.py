from dataclasses import dataclass
from PyQt5 import QtCore
from PyQt5.QtCore import QByteArray, QObject
from PyQt5.QtGui import QImage, QPixmap
from krita import Document, Selection

from .threads import imageThread
from ..client.abstract import Generation

@dataclass
class _image:
  Id: str
  Url: str

class SelectiveGeneration:
  def __init__(self, generation: Generation):
    self.generation = generation
    self.images: dict[str, _image] = {}

    self.selectAll()

  def selectedImages(self):
    return self.images.values()

  def selectAll(self):
    self.images = {}

    for i, image in enumerate(self.generation.GeneratedImages):
      self.images.update({image.Id: _image(image.Id, image.Url)})

      for v, variation in enumerate(image.Variations):
        self.images.update({variation.Id: _image(variation.Id, variation.Url)})

  def onlyImage(self, imagePos: int):
    image = self.generation.GeneratedImages[imagePos]

    self.images = {image.Id: _image(image.Id, image.Url)}
    for v, variation in enumerate(image.Variations):
      self.images.update({variation.Id: _image(variation.Id, variation.Url)})

  def onlyVariation(self, imagePos: int, variationPos: int):
    variation = self.generation.GeneratedImages[imagePos].Variations[variationPos]

    self.images = {variation.Id: _image(variation.Id, variation.Url)}

  def toggleImage(self, imagePos: int):
    gi = self.generation.GeneratedImages[imagePos]

    # remove if given
    if gi.Id in self.images:
      self.images.pop(gi.Id)
      for v in gi.Variations:
        if v.Id in self.images:
          self.images.pop(v.Id)

      return

    # add if missing
    self.images.update({gi.Id: _image(gi.Id, gi.Url)})
    for v in gi.Variations:
      self.images.update({v.Id: _image(v.Id, v.Url)})

class GenerationLoader(QObject):
  sigImageLoaded = QtCore.pyqtSignal(QPixmap, _image)

  def __init__(self,
               document: Document,
               selection: Selection,
               generation: Generation | SelectiveGeneration,
               sigDone: QtCore.pyqtBoundSignal | None = None):
    super().__init__()

    self.document = document
    self.selection = selection
    self.generation = generation
    self.maxImageWidth = 0
    self.maxImageHeight = 0

    if isinstance(generation, Generation): self.sGeneration = SelectiveGeneration(generation)
    else: self.sGeneration = generation

    self.images = {}
    self.imageLoadingThreads = []

    self.grpLayer = self.document.createGroupLayer(f"""AI - {self.sGeneration.generation.Prompt} - {self.sGeneration.generation.Id}""")
    self.document.rootNode().addChildNode(self.grpLayer, None)

    self.sigDone = sigDone
    self.sigImageLoaded.connect(self._onImageLoaded)

  def load(self):
    self.imageLoaded = 0
    self.imageToLoad = len(self.sGeneration.selectedImages())

    # load image in own thread
    for i, image in enumerate(self.sGeneration.selectedImages()):
      il = imageThread(image.Url, self.sigImageLoaded, metaData=image)
      self.imageLoadingThreads.append(il)
      il.start()

  @QtCore.pyqtSlot(QPixmap, _image)
  def _onImageLoaded(self, data: QPixmap, image: _image):
    self.imageLoaded += 1

    layer = self.document.createNode(image.Id, "paintlayer")
    self.grpLayer.addChildNode(layer, None)

    image = QImage(data)
    ptr = image.bits()
    ptr.setsize(image.byteCount())
    layer.setPixelData(
      QByteArray(ptr.asstring()),
      0 if self.selection is None else self.selection.x(),
      0 if self.selection is None else self.selection.y(),
      image.width(),
      image.height(),
    )

    if self.maxImageWidth < image.width(): self.maxImageWidth = image.width()
    if self.maxImageHeight < image.height(): self.maxImageHeight = image.height()

    if self.selection is not None:
      layer.cropNode(self.selection.x(), self.selection.y(), self.selection.width(), self.selection.height())

      invertedSelection = self.selection.duplicate()
      invertedSelection.invert()
      invertedSelection.cut(layer)

    # check if we are done
    if self.imageLoaded == self.imageToLoad:
      # call callback
      if self.sigDone is not None:
        self.sigDone.emit(self.document, self.selection, self.generation, self.maxImageWidth, self.maxImageHeight)
