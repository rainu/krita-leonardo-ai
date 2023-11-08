from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QListWidgetItem
from krita import DockWidget

from ...view.dock import Ui_LeonardoAI
from .ui_settings import Settings
from .model_item import Ui_ModelItem
from ...client.abstract import Model

class BaseDock(DockWidget):
  sigAddModel = QtCore.pyqtSignal(Model)

  def __init__(self):
    super().__init__()
    self.setWindowTitle("Leonardo AI")

    self._modelIdSet = {}
    self.sigAddModel.connect(self._addModel)

    self.ui = Ui_LeonardoAI()
    self.ui.setupUi(self)

    self.ui.lstModel.itemSelectionChanged.connect(self.onMandatoryInputChanges)
    self.ui.inPrompt.textChanged.connect(self.onMandatoryInputChanges)
    self.ui.tabType.currentChanged.connect(self.onTabChange)
    self.ui.settings = Settings(self.onSettingsChanged)

    def onSettingsClick():
      self.ui.settings.show()
      self.ui.settings.setVisible(True)

    self.ui.btnSettings.clicked.connect(onSettingsClick)

  def onSettingsChanged(self):
    pass

  @property
  def model(self) -> Model | None:
    selectedItem = self.ui.lstModel.itemWidget(self.ui.lstModel.currentItem())
    return selectedItem.model if selectedItem is not None else None

  @property
  def prompt(self):
    return self.ui.inPrompt.toPlainText()

  @property
  def negativePrompt(self):
    txt = self.ui.inNegativePrompt.toPlainText()
    return txt if txt != "" else None

  @property
  def numberOfImages(self):
    return self.ui.inNumberOfImages.value()

  @property
  def nsfw(self):
    return self.ui.settings.nsfw

  @property
  def public(self):
    return self.ui.settings.public

  @QtCore.pyqtSlot(Model)
  def _addModel(self, model: Model):
    if model.Id in self._modelIdSet:
      # prevent duplicates
      return

    self._modelIdSet[model.Id] = True

    item = Ui_ModelItem(model)
    wItem = QListWidgetItem(self.ui.lstModel)
    wItem.setSizeHint(QSize(item.sizeHint().width(), item.height()))
    self.ui.lstModel.addItem(wItem)
    self.ui.lstModel.setItemWidget(wItem, item)

  def onMandatoryInputChanges(self):
    self.ui.btnGenerate.setEnabled(self.prompt != "" and self.model is not None)

  def onTabChange(self):
    if self.ui.tabType.currentIndex() == 0: self.onTabText2ImageActivate()
    elif self.ui.tabType.currentIndex() == 1: self.onTabInpaintActivate()
    elif self.ui.tabType.currentIndex() == 2: self.onTabOutpaintActivate()
    elif self.ui.tabType.currentIndex() == 3: self.onTabImage2ImageActivate()
    elif self.ui.tabType.currentIndex() == 4: self.onTabSketch2ImageActivate()


  def onTabText2ImageActivate(self): pass
  def onTabInpaintActivate(self): pass
  def onTabOutpaintActivate(self): pass
  def onTabImage2ImageActivate(self): pass
  def onTabSketch2ImageActivate(self): pass
