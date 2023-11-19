import math
from typing import Callable
from datetime import datetime
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListWidget

from ...client.abstract import Generation, AbstractClient, JobStatus, Model
from ...util.generationLoader import SelectiveGeneration
from ...view.generation_search import Ui_GenerationSearch
from ...util.threads import GeneralThread
from .generation_search_item import GenerationSearchItem
from .model_item import ModelItem

class GenerationSearch(QtWidgets.QDialog):
  userId = None

  sigAddGenerationResultItems = QtCore.pyqtSignal(list)

  def __init__(self,
               getLeonardoAI: Callable[[], AbstractClient],
               refModels: QListWidget,
               choseGenerationCallback: Callable[[SelectiveGeneration], None]):
    super().__init__()
    self.setWindowTitle("Leonardo AI - Generation")

    self.sigAddGenerationResultItems.connect(self._addResultItems)
    self.getLeonardoAI = getLeonardoAI
    self.choseGenerationCallback = choseGenerationCallback
    self.searchThread = None

    self.ui = Ui_GenerationSearch()
    self.ui.setupUi(self)
    self.refModels = refModels

    def onHeightChanges():
      self.ui.inHeightMin.setEnabled(self.ui.chkHeight.isChecked())
      self.ui.inHeightMax.setEnabled(self.ui.chkHeight.isChecked())

    self.ui.chkHeight.stateChanged.connect(onHeightChanges)

    def onWidthChanges():
      self.ui.inWidthMin.setEnabled(self.ui.chkWidth.isChecked())
      self.ui.inWidthMax.setEnabled(self.ui.chkWidth.isChecked())

    self.ui.chkWidth.stateChanged.connect(onWidthChanges)

    def onLikesChanges():
      self.ui.inLikesMin.setEnabled(self.ui.chkLikes.isChecked())
      self.ui.inLikesMax.setEnabled(self.ui.chkLikes.isChecked())

    self.ui.chkLikes.stateChanged.connect(onLikesChanges)

    now = datetime.now()
    self.ui.inCreatedAtMin.setDateTime(now)
    self.ui.inCreatedAtMin.setMaximumDate(now)
    self.ui.inCreatedAtMax.setDateTime(now)
    self.ui.inCreatedAtMax.setMaximumDate(now)

    self.offset = 0
    self.limit = 50

    def onSearch():
      self.offset = 0
      self.onGenerationSearchClicked()

    self.ui.btnSearch.clicked.connect(onSearch)

    def onPagePrev():
      self.offset = max(0, self.offset - self.limit)
      self.onGenerationSearchClicked()

    self.ui.btnPagePrev.clicked.connect(onPagePrev)

    def onPageNext():
      self.offset += self.limit
      self.onGenerationSearchClicked()

    self.ui.btnPageNext.clicked.connect(onPageNext)
    self.ui.grpPage.setVisible(False)

  def showEvent(self, event):
    super().showEvent(event)

    # need to decide if generation is owned by the user
    self.userId = self.getLeonardoAI().getUserInfo().Id

    columnCount = self.ui.tblModel.columnCount()
    self.ui.tblModel.setRowCount(math.ceil(self.refModels.count() / columnCount))
    for i in range(self.refModels.count()):
      tRow = i // columnCount
      tCol = i % columnCount

      # skip models which are already known
      if self.ui.tblModel.cellWidget(tRow, tCol) is not None: continue

      foreignItem = self.refModels.itemWidget(self.refModels.item(i))
      item = ModelItem(foreignItem.model)
      self.ui.tblModel.setCellWidget(tRow, tCol, item)
      self.ui.tblModel.setColumnWidth(tCol, item.width())
      self.ui.tblModel.setRowHeight(tRow, item.height())

  @property
  def selectedModels(self) -> list[Model]:
    selected_indexes = self.ui.tblModel.selectedIndexes()
    selected_cells = [(index.row(), index.column()) for index in selected_indexes]

    models = []
    for [cRow, cCol] in selected_cells:
      widget = self.ui.tblModel.cellWidget(cRow, cCol)
      if widget is not None: models.append(widget.model)

    return models

  def onGenerationSearchClicked(self):
    if self.searchThread is not None and self.searchThread.isRunning():
      return

    self._clearResults()

    self.searchThread = GeneralThread(self.search, self.sigAddGenerationResultItems)
    self.searchThread.start()

  def search(self, q: GeneralThread) -> list[Generation]:
    args = {
      "status": JobStatus.COMPLETE,
      "community": self.ui.radCommunity.isChecked(),
      "modelIds": [model.Id for model in self.selectedModels],
      "offset": self.offset, "limit": self.limit,
    }

    if self.ui.inPrompt.text() != "": args.update({"prompt": self.ui.inPrompt.text()})
    if self.ui.inNegativePrompt.text() != "": args.update({"negativePrompt": self.ui.inNegativePrompt.text()})
    if self.ui.chkWidth.isChecked():
      args.update({"minImageWidth": self.ui.inWidthMin.value(), "maxImageWidth": self.ui.inWidthMax.value()})
    if self.ui.chkHeight.isChecked():
      args.update({"minImageHeight": self.ui.inHeightMin.value(), "maxImageHeight": self.ui.inHeightMax.value()})
    if self.ui.chkLikes.isChecked():
      args.update({"minLikeCount": self.ui.inLikesMin.value(), "maxLikeCount": self.ui.inLikesMax.value()})
    if not self.ui.radNSFWBoth.isChecked():
      args.update({"notSafeForWork": self.ui.radNSFWNotSafe.isChecked()})
    if self.ui.grpCreatedAt.isChecked():
      args.update({"minCreatedAt": self.ui.inCreatedAtMin.dateTime().toPyDateTime(), "maxCreatedAt": self.ui.inCreatedAtMax.dateTime().toPyDateTime()})

    if self.ui.cmbOrderBy.currentIndex() == 0: args.update({ "orderByCreatedAsc": False })
    elif self.ui.cmbOrderBy.currentIndex() == 1: args.update({ "orderByCreatedAsc": True })
    elif self.ui.cmbOrderBy.currentIndex() == 2: args.update({ "orderByLikesAsc": False })
    elif self.ui.cmbOrderBy.currentIndex() == 3: args.update({ "orderByLikesAsc": True })

    return self.getLeonardoAI().getGenerations(**args)


  def _clearResults(self):
    while self.ui.frmResults.layout().count():
      item = self.ui.frmResults.layout().takeAt(0)
      widget = item.widget()
      if widget: widget.deleteLater()

  @QtCore.pyqtSlot(list)
  def _addResultItems(self, generations: list[Generation]):
    for generation in generations:
      item = GenerationSearchItem(self.userId, generation)
      item.connectLoad(self.onGenerationSearchItemLoad)
      item.connectDelete(self.onGenerationSearchItemDelete)
      item.setDoubleClickListener(self.onGenerationSelected)

      self.ui.frmResults.layout().addWidget(item)

    self.ui.grpPage.setVisible(self.offset > 0 or len(generations) >= self.limit)
    self.ui.btnPagePrev.setEnabled(self.offset > 0)
    self.ui.btnPageNext.setEnabled(len(generations) >= self.limit)

  def onGenerationSearchItemLoad(self, item: GenerationSearchItem):
    self.choseGenerationCallback(item.selectiveGeneration)

  def onGenerationSearchItemDelete(self, item: GenerationSearchItem):
    self.getLeonardoAI().deleteGenerationById(item.generation.Id)
    self.ui.frmResults.layout().removeWidget(item)
    item.setParent(None)
    item.deleteLater()

  def onGenerationSelected(self, sGeneration: SelectiveGeneration):
    self.choseGenerationCallback(sGeneration)
    self.setVisible(False)