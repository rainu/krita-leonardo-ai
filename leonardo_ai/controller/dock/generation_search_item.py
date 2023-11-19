from typing import Callable
from dataclasses import dataclass
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QTabWidget
from ...client.abstract import Generation
from ...util.generationLoader import SelectiveGeneration
from ...view.generation_search_item import Ui_GenerationSearchItem
from ...util.threads import imageThread

@dataclass
class ImageVariationMeta:
  ImagePos: int
  VariationPos: int

# TODO: support more than 4 image generations
MAX_IMAGE = 4

class GenerationSearchItem(QWidget):
  sigImageChange = QtCore.pyqtSignal(QPixmap, int)
  sigImageVariationChange = QtCore.pyqtSignal(QPixmap, ImageVariationMeta)
  dcCallback: Callable[[SelectiveGeneration], None] = None

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

    def onToggleFactory(btn, index: int):
      def onToggle():
        self.selectiveGeneration.toggleImageAndVariations(index)
        btn.setChecked(btn.isChecked())

      return onToggle

    for i in range(MAX_IMAGE):
      btn = self.ui.__dict__.get(f"""btnGfxLoad{i}""")
      btn.setVisible(False)
      btn.setChecked(True)

      btn.clicked.connect(onToggleFactory(btn, i))

      tabs = self.ui.__dict__.get(f"""tabVariations{i}""")
      tabs.setVisible(False)
      tabs.currentChanged.connect(self._buildOnTabChangedHandler(i, tabs))
      tabs.tabCloseRequested.connect(self._buildOnTabCloseHandler(i, tabs))

    for i, image in enumerate(generation.GeneratedImages):
      if i >= MAX_IMAGE: break

      gfx = self.ui.__dict__.get(f"""gfx{i}""")
      if gfx is not None: gfx.setText("loading...")

      lblLikes = self.ui.__dict__.get(f"""lblLikeCount{i}""")
      if lblLikes is not None: lblLikes.setText(f"""{image.LikeCount} likes""")

      tabs = self.ui.__dict__.get(f"""tabVariations{i}""")
      tabs.setVisible(True)

      for v, variation in enumerate(image.Variations):
        tab = QWidget()
        tab.setObjectName(f"""tabImage{i}Variation{v}""")

        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setObjectName(f"""layout{tab.objectName()}""")

        vGfx = QLabel(tab)
        vGfx.setSizePolicy(gfx.sizePolicy())
        vGfx.setText("loading...")
        vGfx.setAlignment(QtCore.Qt.AlignCenter)
        vGfx.setObjectName(f"""gfx{i}Variation{v}""")
        self.ui.__dict__.update({vGfx.objectName(): vGfx})
        layout.addWidget(vGfx)

        tabs.addTab(tab, "")
        tabs.setTabText(v + 1, f"""#{v + 2}""")

    self.sigImageChange.connect(self._onImageChange)
    self.sigImageVariationChange.connect(self._onImageVariationChange)

    self.imageThreads = []
    self.loadedImages = 0
    for i, image in enumerate(self.generation.GeneratedImages):
      if i >= MAX_IMAGE: break

      t = imageThread(image.Url, self.sigImageChange, metaData=i)
      t.start()
      self.imageThreads.append(t)

  def deleteLater(self):
    for it in self.imageThreads: it.terminate()

    super().deleteLater()

  def connectDelete(self, clb: Callable):
    def onClick(): clb(self)
    self.ui.btnDelete.clicked.connect(onClick)

  def connectLoad(self, clb: Callable):
    def onClick(): clb(self)
    self.ui.btnLoad.clicked.connect(onClick)

  def _buildOnTabChangedHandler(self, imagePos: int, tabs: QTabWidget):
    def handle():
      self.onTabChanged(imagePos, tabs)

    return handle

  def _buildOnTabCloseHandler(self, imagePos: int, tabs: QTabWidget):
    def handle(index):
      self.onTabClosed(imagePos, tabs, index)

    return handle

  def onTabChanged(self, imagePos: int, tabs: QTabWidget):
    variation = tabs.currentIndex() - 1
    lblTarget = self.ui.__dict__.get(f"""gfx{imagePos}Variation{variation}""")
    if lblTarget is not None:
      t = imageThread(self.generation.GeneratedImages[imagePos].Variations[variation].Url,
                      self.sigImageVariationChange, metaData=ImageVariationMeta(imagePos, variation))
      t.start()
      self.imageThreads.append(t)

  def onTabClosed(self, imagePos: int, tabs: QTabWidget, index: int):
    if tabs.tabBar().tabTextColor(index) == QColor("red"): tabs.tabBar().setTabTextColor(index, QColor())
    else: tabs.tabBar().setTabTextColor(index, QColor("red"))

    if index == 0:
      self.selectiveGeneration.toggleImage(imagePos)
    else:
      self.selectiveGeneration.toggleImageVariation(imagePos, index - 1)

  @QtCore.pyqtSlot(QPixmap, int)
  def _onImageChange(self, data: QPixmap, pos: int):
    lblTarget = self.ui.__dict__.get(f"""gfx{pos}""")
    if lblTarget is not None:
      lblTarget.setPixmap(data.scaled(250, data.size().height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))

      def onDoubleClick(event):
        if self.dcCallback is not None:
          sg = SelectiveGeneration(self.generation)
          sg.onlyImage(pos)

          self.dcCallback(sg)

      lblTarget.mouseDoubleClickEvent = onDoubleClick

    btnTarget = self.ui.__dict__.get(f"""btnGfxLoad{pos}""")
    if btnTarget is not None:
      btnTarget.setVisible(True)

    # enable load-button after all images are loaded
    self.loadedImages += 1
    self.ui.btnLoad.setEnabled(self.loadedImages == len(self.generation.GeneratedImages))

  @QtCore.pyqtSlot(QPixmap, ImageVariationMeta)
  def _onImageVariationChange(self, data: QPixmap, pos: ImageVariationMeta):
    lblTarget = self.ui.__dict__.get(f"""gfx{pos.ImagePos}Variation{pos.VariationPos}""")
    if lblTarget is not None:
      lblTarget.setPixmap(data.scaled(250, data.size().height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))

      def onDoubleClick(event):
        if self.dcCallback is not None:
          sg = SelectiveGeneration(self.generation)
          sg.onlyVariation(pos.ImagePos, pos.VariationPos)

          self.dcCallback(sg)

      lblTarget.mouseDoubleClickEvent = onDoubleClick

  def setDoubleClickListener(self, callback: Callable[[SelectiveGeneration], None]):
    self.dcCallback = callback
