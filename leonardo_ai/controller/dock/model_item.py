import requests
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from ...client.abstract import Model
from ...view.model_item import Ui_modelItem
from ...util.thread import Thread


class Ui_ModelItem(QWidget):
  sigImageChange = QtCore.pyqtSignal(QPixmap)

  def __init__(self, aiModel: Model):
    super(Ui_ModelItem, self).__init__()

    self.model = aiModel
    self.ui = Ui_modelItem()
    self.ui.setupUi(self)

    self.ui.lblBase.setText(aiModel.StableDiffusionVersion)
    self.ui.lblName.setText(aiModel.Name)
    self.ui.lblModelDim.setText(f"""{aiModel.Width}x{aiModel.Height}""")
    self.setToolTip(aiModel.Description)

    self.sigImageChange.connect(self._onImageChange)

    self.loadingThread = Thread(target=self._loadImage)
    self.loadingThread.start()

  def _loadImage(self):
    try:
      data = requests.get(self.model.PreviewImage.Url).content
      pixmap = QPixmap()
      pixmap.loadFromData(data)

      self.sigImageChange.emit(pixmap)
    except Exception as e:
      print("Unable to load image: ", e)

  @QtCore.pyqtSlot(QPixmap)
  def _onImageChange(self, data: QPixmap):
    ms = self.ui.gfxIcon.maximumSize()

    self.previewImg = data
    self.ui.gfxIcon.setPixmap(self.previewImg.scaled(ms.width(), ms.height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))
