from typing import Callable
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from ...client.abstract import Generation
from ...view.generation_search_item import Ui_GenerationSearchItem
from ...util.threads import imageThread


class GenerationSearchItem(QWidget):
  sigImageChange = QtCore.pyqtSignal(QPixmap, int)
  dcCallback: Callable[[Generation, int], None] = None

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
      self.ui.lblCreator.setText(f"""Creator: {generation.GeneratedImages[0].Creator.Name}""")
      self.ui.btnDelete.setVisible(generation.GeneratedImages[0].Creator.Id == userId)

    self.selectedImages: dict[int, bool] = {}

    def onToggleFactory(btn, index: int):
      def onToggle():
        self.selectedImages[index] = not self.selectedImages[index]
        btn.setChecked(self.selectedImages[index])

      return onToggle

    for i in range(4):
      btn = self.ui.__dict__.get(f"""btnGfxLoad{i}""")
      btn.setVisible(False)
      btn.setChecked(True)
      self.selectedImages[i] = True

      btn.clicked.connect(onToggleFactory(btn, i))

    for i, image in enumerate(generation.GeneratedImages):
      gfx = self.ui.__dict__.get(f"""gfx{i}""")
      if gfx is not None: gfx.setText("loading...")

      lblLikes = self.ui.__dict__.get(f"""lblLikeCount{i}""")
      if lblLikes is not None: lblLikes.setText(f"""{image.LikeCount} likes""")

    self.sigImageChange.connect(self._onImageChange)

    self.imageThreads = []
    for i, image in enumerate(self.generation.GeneratedImages):
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

  @QtCore.pyqtSlot(QPixmap, int)
  def _onImageChange(self, data: QPixmap, pos: int):
    lblTarget = self.ui.__dict__.get(f"""gfx{pos}""")
    if lblTarget is not None:
      lblTarget.setPixmap(data.scaled(250, data.size().height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))

      def onDoubleClick(event):
        if self.dcCallback is not None: self.dcCallback(self.generation, pos)

      lblTarget.mouseDoubleClickEvent = onDoubleClick

    btnTarget = self.ui.__dict__.get(f"""btnGfxLoad{pos}""")
    if btnTarget is not None:
      btnTarget.setVisible(True)

  def setDoubleClickListener(self, callback: Callable[[Generation, int], None]):
    self.dcCallback = callback
