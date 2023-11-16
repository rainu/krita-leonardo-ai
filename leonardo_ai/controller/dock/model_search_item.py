from typing import Callable
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from ...client.abstract import Model
from ...view.model_search_item import Ui_ModelSearchItem
from ...util.threads import imageThread


class ModelSearchItem(QWidget):
  sigImageChange = QtCore.pyqtSignal(QPixmap)
  dcCallback = None

  def __init__(self, aiModel: Model):
    super(ModelSearchItem, self).__init__()

    self.model = aiModel
    self.ui = Ui_ModelSearchItem()
    self.ui.setupUi(self)

    self.ui.lblName.setText(aiModel.Name)
    self.ui.lblDescription.setText(aiModel.Description)
    self.ui.lblUser.setText(aiModel.User.Name)

    self.sigImageChange.connect(self._onImageChange)

    self.loadingThread = imageThread(self.model.PreviewImage.Url, self.sigImageChange)
    self.loadingThread.start()

  def deleteLater(self):
    self.loadingThread.terminate()

    super().deleteLater()

  @QtCore.pyqtSlot(QPixmap)
  def _onImageChange(self, data: QPixmap):
    self.ui.lblImage.setPixmap(data.scaled(250, data.size().height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))

  def setDoubleClickListener(self, callback: Callable[[Model], None]):
    self.dcCallback = callback

  def mouseDoubleClickEvent(self, event):
    if self.dcCallback is not None: self.dcCallback(self.model)