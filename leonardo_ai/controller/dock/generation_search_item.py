from typing import Callable
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from .generation_search_item_image import GenerationSearchItemImage
from ...client.abstract import Generation
from ...util.generationLoader import SelectiveGeneration
from ...view.generation_search_item import Ui_GenerationSearchItem

class GenerationSearchItem(QWidget):
  sigImageChange = QtCore.pyqtSignal(QPixmap, int)

  def __init__(self, userId: str, generation: Generation):
    super(GenerationSearchItem, self).__init__()

    self.userId = userId
    self.generation = generation
    self.ui = Ui_GenerationSearchItem()
    self.ui.setupUi(self)

    self.ui.lblPrompt.setText(generation.Prompt)
    self.ui.lblNegativePrompt.setText(generation.NegativePrompt)
    self.ui.lblImageDim.setText(f"""Dimension: {generation.ImageWidth}x{generation.ImageHeight}px""")

    if generation.CustomModel is not None:
      self.ui.lblModelName.setText(f"""Model: {generation.CustomModel.Name}""")
    else:
      self.ui.lblModelName.setText(f"""Model: StableDiffusion {generation.SDVersion.replace("_",".")}""")

    if len(generation.GeneratedImages) > 0:
      self.ui.lblCreator.setText(f"""Creator: {generation.GeneratedImages[0].Creator.Name} ({ "public" if generation.Public else "private" })""")
      self.ui.btnDelete.setVisible(generation.GeneratedImages[0].Creator.Id == userId)

    self.selectiveGeneration = SelectiveGeneration(generation)
    self.imageWidgets = []

    for i, image in enumerate(self.generation.GeneratedImages):
      imageWidget = GenerationSearchItemImage(self.selectiveGeneration, image, i)
      imageWidget.setMaximumSize(imageWidget.width(), imageWidget.height())
      self.ui.frmImages.layout().addWidget(imageWidget, i // 4, i % 4, 1, 1)
      self.imageWidgets.append(imageWidget)

  def deleteLater(self):
    for imageWidget in self.imageWidgets: imageWidget.deleteLater()

    super().deleteLater()

  def connectDelete(self, clb: Callable):
    def onClick(): clb(self)
    self.ui.btnDelete.clicked.connect(onClick)

  def connectLoad(self, clb: Callable):
    def onClick(): clb(self)
    self.ui.btnLoad.clicked.connect(onClick)

  def setDoubleClickListener(self, callback: Callable[[SelectiveGeneration], None]):
    for imageWidget in self.imageWidgets:
      imageWidget.setDoubleClickListener(callback)
