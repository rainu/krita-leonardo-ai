from typing import Callable
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from ...client.abstract import Image
from ...util.generationLoader import SelectiveGeneration
from ...view.generation_search_item_image import Ui_GenerationSearchItemImage
from ...util.threads import imageThread

class GenerationSearchItemImage(QWidget):
  sigImageLoaded = QtCore.pyqtSignal(QPixmap)
  sigVariationLoaded = QtCore.pyqtSignal(QPixmap, int)
  dcCallback: Callable[[SelectiveGeneration], None] = None

  def __init__(self, sGeneration: SelectiveGeneration, image: Image, imageNr: int):
    super(GenerationSearchItemImage, self).__init__()

    self.selectiveGeneration = sGeneration
    self.image = image
    self.imageNr = imageNr
    self.ui = Ui_GenerationSearchItemImage()
    self.ui.setupUi(self)

    self.ui.btnGfxLoad.setChecked(True)
    self.ui.btnGfxLoad.clicked.connect(self.onLoadToggle)

    self.ui.tabVariations.currentChanged.connect(self.onTabChanged)
    self.ui.tabVariations.tabCloseRequested.connect(self.onTabClosed)

    self.ui.lblLikeCount.setText(f"""{image.LikeCount} likes""")

    for v, variation in enumerate(image.Variations):
      tab = QWidget()
      tab.setObjectName(f"""tabImageVariation{v}""")

      layout = QHBoxLayout(tab)
      layout.setContentsMargins(0, 0, 0, 0)
      layout.setSpacing(0)
      layout.setObjectName(f"""layout{tab.objectName()}""")

      vGfx = QLabel(tab)
      vGfx.setSizePolicy(self.ui.gfx.sizePolicy())
      vGfx.setText("loading...")
      vGfx.setAlignment(QtCore.Qt.AlignCenter)
      vGfx.setObjectName(f"""gfxVariation{v}""")
      self.ui.__dict__.update({vGfx.objectName(): vGfx})
      layout.addWidget(vGfx)

      self.ui.tabVariations.addTab(tab, "")
      self.ui.tabVariations.setTabText(v + 1, f"""#{v + 2}""")

    self.sigImageLoaded.connect(self._onImageLoaded)
    self.sigVariationLoaded.connect(self._onVariationLoaded)

    self.imageThreads = [imageThread(image.Url, self.sigImageLoaded)]
    self.imageThreads[0].start()

  def deleteLater(self):
    for it in self.imageThreads: it.terminate()

    super().deleteLater()

  def onLoadToggle(self):
    self.selectiveGeneration.toggleImageAndVariations(self.imageNr)
    self.ui.btnGfxLoad.setChecked(self.ui.btnGfxLoad.isChecked())

  def onTabChanged(self, index: int):
    lblTarget = self.ui.__dict__.get(f"""gfxVariation{index}""")
    if lblTarget is not None:
      t = imageThread(self.image.Variations[index].Url, self.sigVariationLoaded, metaData=index)
      t.start()
      self.imageThreads.append(t)

  def onTabClosed(self, index: int):
    if self.ui.tabVariations.tabBar().tabTextColor(index) == QColor("red"):
      self.ui.tabVariations.tabBar().setTabTextColor(index, QColor())
    else:
      self.ui.tabVariations.tabBar().setTabTextColor(index, QColor("red"))

    if index == 0:
      self.selectiveGeneration.toggleImage(self.imageNr)
    else:
      self.selectiveGeneration.toggleImageVariation(self.imageNr, index - 1)

  @QtCore.pyqtSlot(QPixmap)
  def _onImageLoaded(self, data: QPixmap):
    self.ui.gfx.setPixmap(data.scaled(
      250,
      data.size().height(),
      QtCore.Qt.AspectRatioMode.KeepAspectRatio
    ))

    def onDoubleClick(event):
      if self.dcCallback is not None:
        sg = SelectiveGeneration(self.selectiveGeneration.generation)
        sg.onlyImage(self.imageNr)

        self.dcCallback(sg)

    self.ui.gfx.mouseDoubleClickEvent = onDoubleClick

    self.ui.btnGfxLoad.setVisible(True)

  @QtCore.pyqtSlot(QPixmap, int)
  def _onVariationLoaded(self, data: QPixmap, variationNr: int):
    lblTarget = self.ui.__dict__.get(f"""gfxVariation{variationNr}""")
    if lblTarget is not None:
      lblTarget.setPixmap(data.scaled(
        250,
        data.height(),
        QtCore.Qt.AspectRatioMode.KeepAspectRatio,
      ))

      def onDoubleClick(event):
        if self.dcCallback is not None:
          sg = SelectiveGeneration(self.selectiveGeneration.generation)
          sg.onlyVariation(self.imageNr, variationNr)

          self.dcCallback(sg)

      lblTarget.mouseDoubleClickEvent = onDoubleClick

  def setDoubleClickListener(self, callback: Callable[[SelectiveGeneration], None]):
    self.dcCallback = callback
