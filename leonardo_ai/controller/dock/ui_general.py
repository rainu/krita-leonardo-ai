from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QListWidgetItem
from krita import DockWidget

from ...view.dock import Ui_LeonardoAI
from .ui_settings import Settings
from .ui_modelSearch import ModelSearch
from .ui_generationSearch import GenerationSearch
from .model_item import ModelItem
from ...client.abstract import Generation, Model, AbstractClient

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

    def onModelSearchSelect(model: Model):
      self._addModel(model)
      self.selectModelById(model.Id)

    self.ui.modelSearch = ModelSearch(self.getLeonardoAI, onModelSearchSelect)

    def onModelSearchClick():
      self.ui.modelSearch.show()
      self.ui.modelSearch.setVisible(True)

    self.ui.btnModelSearch.clicked.connect(onModelSearchClick)

    self.ui.cmbPresetStyle.setVisible(True)
    self.ui.cmbAlchemyPresetStyle.setVisible(False)
    self.ui.inPrompt.textChanged.connect(self.onMandatoryInputChanges)

    self.ui.btnGenerate.clicked.connect(self.onGenerate)
    self.ui.btnInterrupt.clicked.connect(self.onInterrupt)
    self.ui.btnInterrupt.setVisible(False)

    self.ui.generationSearch = GenerationSearch(self.getLeonardoAI, self.ui.lstModel, self.onLoadGeneration)

    def onGenerationSearchClick():
      self.ui.generationSearch.show()
      self.ui.generationSearch.setVisible(True)

    self.ui.btnGenerateSearch.clicked.connect(onGenerationSearchClick)

    def onModeChange():
      self.ui.grpText2Image.setVisible(self.ui.cmbMode.currentIndex() == 0)
      self.ui.grpInpaint.setVisible(self.ui.cmbMode.currentIndex() == 1)
      self.ui.grpImage2Image.setVisible(self.ui.cmbMode.currentIndex() == 3)
      self.ui.grpSketch2Image.setVisible(self.ui.cmbMode.currentIndex() == 4)

    self.ui.cmbMode.currentIndexChanged.connect(onModeChange)
    onModeChange()

    self.ui.settings = Settings(self.onSettingsChanged)

    def onSettingsClick():
      self.ui.settings.show()
      self.ui.settings.setVisible(True)

    self.ui.btnSettings.clicked.connect(onSettingsClick)

  def selectModelById(self, modelId: str):
    for i in range(self.ui.lstModel.count()):
      item = self.ui.lstModel.item(i)
      wItem = self.ui.lstModel.itemWidget(item)
      if wItem.model.Id == modelId:
        item.setSelected(True)
        self.ui.lstModel.scrollToItem(item)
        break

  def getLeonardoAI(self) -> AbstractClient:
    pass

  def onGenerate(self):
    self.ui.btnGenerate.setVisible(False)
    self.ui.btnInterrupt.setVisible(True)

  def onInterrupt(self):
    self.ui.btnGenerate.setVisible(True)
    self.ui.btnInterrupt.setVisible(False)

  def onSettingsChanged(self):
    pass

  def onLoadGeneration(self, generation: Generation, selectedImages: dict[int, bool] | None):
    pass

  @property
  def model(self) -> Model | None:
    selectedItem = self.ui.lstModel.itemWidget(self.ui.lstModel.currentItem())
    return selectedItem.model if selectedItem is not None else None

  @property
  def presetStyle(self):
    if self.ui.cmbPresetStyle.isVisible():
      if self.ui.cmbPresetStyle.currentIndex() == 0: return None
      else: return self.ui.cmbPresetStyle.currentText().upper()

    elif self.ui.cmbAlchemyPresetStyle.isVisible():
      if self.ui.cmbAlchemyPresetStyle.currentIndex() == 0: return None
      if not self.ui.cmbAlchemyPresetStyle.currentText().__contains__(" "): return self.ui.cmbAlchemyPresetStyle.currentText().upper()
      else:
        label = self.ui.cmbAlchemyPresetStyle.currentText()
        if label == "Sketch B/W": return "SKETCH_BW"
        elif label == "Sketch Color": return "SKETCH_COLOR"
        elif label == "3D Render": return "RENDER_3D"

    return None

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

    item = ModelItem(model)
    wItem = QListWidgetItem(self.ui.lstModel)
    wItem.setSizeHint(QSize(item.sizeHint().width(), item.height()))
    self.ui.lstModel.addItem(wItem)
    self.ui.lstModel.setItemWidget(wItem, item)

  def onMandatoryInputChanges(self):
    self.ui.btnGenerate.setEnabled(self.prompt != "" and self.model is not None)
