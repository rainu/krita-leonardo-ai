from typing import Callable
from datetime import datetime
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from ...client.abstract import Generation, AbstractClient, JobStatus
from ...view.generation_search import Ui_GenerationSearch
from ...util.thread import Thread
from .generation_search_item import GenerationSearchItem

class GenerationSearch(QtWidgets.QDialog):
  sigAddGenerationResultItems = QtCore.pyqtSignal(list)

  def __init__(self, getLeonardoAI: Callable[[], AbstractClient], choseGenerationCallback: Callable[[Generation, dict[int, bool] | None], None]):
    super().__init__()
    self.setWindowTitle("Leonardo AI - Generation")

    self.sigAddGenerationResultItems.connect(self._addResultItems)
    self.getLeonardoAI = getLeonardoAI
    self.choseGenerationCallback = choseGenerationCallback
    self.searchThread = None

    self.ui = Ui_GenerationSearch()
    self.ui.setupUi(self)

    def onHeightChanges():
      self.ui.inHeightMin.setEnabled(self.ui.chkHeight.isChecked())
      self.ui.inHeightMax.setEnabled(self.ui.chkHeight.isChecked())

    self.ui.chkHeight.stateChanged.connect(onHeightChanges)

    def onWidthChanges():
      self.ui.inWidthMin.setEnabled(self.ui.chkWidth.isChecked())
      self.ui.inWidthMax.setEnabled(self.ui.chkWidth.isChecked())

    self.ui.chkWidth.stateChanged.connect(onWidthChanges)

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

  def onGenerationSearchClicked(self):
    if self.searchThread is not None and self.searchThread.isRunning():
      return

    self._clearResults()

    def run(q): self.sigAddGenerationResultItems.emit(self.search())

    self.searchThread = Thread(run)
    self.searchThread.start()

  def search(self):
    args = {
      "status": JobStatus.COMPLETE,
      "orderByCreatedAsc": self.ui.cmbCreatedAt.currentIndex() == 1,
      "offset": self.offset, "limit": self.limit,
    }
    if self.ui.inPrompt.text() != "": args.update({"prompt": self.ui.inPrompt.text()})
    if self.ui.inNegativePrompt.text() != "": args.update({"negativePrompt": self.ui.inNegativePrompt.text()})
    if self.ui.chkWidth.isChecked():
      args.update({"minImageWidth": self.ui.inWidthMin.value(), "maxImageWidth": self.ui.inWidthMax.value()})
    if self.ui.chkHeight.isChecked():
      args.update({"minImageHeight": self.ui.inHeightMin.value(), "maxImageHeight": self.ui.inHeightMax.value()})
    if self.ui.grpCreatedAt.isChecked():
      args.update({"minCreatedAt": self.ui.inCreatedAtMin.dateTime().toPyDateTime(), "maxCreatedAt": self.ui.inCreatedAtMax.dateTime().toPyDateTime()})

    return self.getLeonardoAI().getGenerations(**args)


  def _clearResults(self):
    while self.ui.frmResults.layout().count():
      item = self.ui.frmResults.layout().takeAt(0)
      widget = item.widget()
      if widget: widget.deleteLater()

  @QtCore.pyqtSlot(list)
  def _addResultItems(self, generations: list[Generation]):
    for generation in generations:
      item = GenerationSearchItem(generation)
      item.connectLoad(self.onGenerationSearchItemLoad)
      item.connectDelete(self.onGenerationSearchItemDelete)
      item.setDoubleClickListener(self.onGenerationSelected)

      self.ui.frmResults.layout().addWidget(item)

    self.ui.grpPage.setVisible(self.offset > 0 or len(generations) >= self.limit)
    self.ui.btnPagePrev.setEnabled(self.offset > 0)
    self.ui.btnPageNext.setEnabled(len(generations) >= self.limit)

  def onGenerationSearchItemLoad(self, item: GenerationSearchItem):
    self.choseGenerationCallback(item.generation, item.selectedImages)

  def onGenerationSearchItemDelete(self, item: GenerationSearchItem):
    self.getLeonardoAI().deleteGenerationById(item.generation.Id)
    self.ui.frmResults.layout().removeWidget(item)
    item.setParent(None)
    item.deleteLater()

  def onGenerationSelected(self, generation: Generation, imgIndex: int):
    selectedImages = {}
    for i in range(len(generation.GeneratedImages)): selectedImages[i] = False
    selectedImages[imgIndex] = True

    self.choseGenerationCallback(generation, selectedImages)
    self.setVisible(False)