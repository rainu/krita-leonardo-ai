import requests
from typing import Callable
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from ...client.abstract import Generation
from ...view.generation_search_item import Ui_GenerationSearchItem
from ...util.thread import Thread

class GenerationSearchItem(QWidget):
  sigImageChange = QtCore.pyqtSignal(int, QPixmap)
  dcCallback: Callable[[Generation, int], None] = None

  def __init__(self, generation: Generation):
    super(GenerationSearchItem, self).__init__()

    self.generation = generation
    self.ui = Ui_GenerationSearchItem()
    self.ui.setupUi(self)

    self.ui.lblPrompt.setText(generation.Prompt)
    self.ui.lblNegativePrompt.setText(generation.NegativePrompt)
    self.ui.lblImageDim.setText(f"""{generation.ImageWidth}x{generation.ImageHeight}px""")

    if generation.CustomModel is not None:
      self.ui.lblModelName.setText(generation.CustomModel.Name)
    else:
      self.ui.lblModelName.setText(f"""StableDiffusion {generation.SDVersion.replace("_",".")}""")

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

    for i, _ in enumerate(generation.GeneratedImages):
      self.ui.__dict__.get(f"""gfx{i}""").setText("loading...")

    self.sigImageChange.connect(self._onImageChange)

    self.loadingThread = Thread(target=self._loadImages)
    self.loadingThread.start()

  def connectDelete(self, clb: Callable):
    def onClick(): clb(self)
    self.ui.btnDelete.clicked.connect(onClick)

  def connectLoad(self, clb: Callable):
    def onClick(): clb(self)
    self.ui.btnLoad.clicked.connect(onClick)

  def _loadImages(self, t):
    try:
      for i, image in enumerate(self.generation.GeneratedImages):
        data = requests.get(image.Url).content
        pixmap = QPixmap()
        pixmap.loadFromData(data)

        self.sigImageChange.emit(i, pixmap)
    except Exception as e:
      print("Unable to load image: ", e)

  @QtCore.pyqtSlot(int, QPixmap)
  def _onImageChange(self, pos: int, data: QPixmap):
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
