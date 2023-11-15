from typing import Callable

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from ...client.abstract import Model, AbstractClient
from ...view.model_search import Ui_ModelSearch
from ...util.threads import GeneralThread
from .model_search_item import ModelSearchItem

class ModelSearch(QtWidgets.QDialog):
  sigAddModelResultItem = QtCore.pyqtSignal(Model)

  def __init__(self, getLeonardoAI: Callable[[], AbstractClient], choseModelCallback: Callable[[Model], None]):
    super().__init__()
    self.setWindowTitle("Leonardo AI - Model")

    self.sigAddModelResultItem.connect(self._addResultItem)
    self.getLeonardoAI = getLeonardoAI
    self.choseModelCallback = choseModelCallback
    self.searchThread = None

    self.ui = Ui_ModelSearch()
    self.ui.setupUi(self)

    def enableAll():
      self.ui.btnModelPlattform.setEnabled(True)
      self.ui.btnModelYour.setEnabled(True)
      self.ui.btnModelFavorite.setEnabled(True)
      self.ui.btnModelCommunity.setEnabled(True)

    def onPlatformClick():
      enableAll()
      self.ui.btnModelPlattform.setEnabled(False)

    self.ui.btnModelPlattform.clicked.connect(onPlatformClick)

    def onYourClick():
      enableAll()
      self.ui.btnModelYour.setEnabled(False)

    self.ui.btnModelYour.clicked.connect(onYourClick)

    def onFavoriteClick():
      enableAll()
      self.ui.btnModelFavorite.setEnabled(False)

    self.ui.btnModelFavorite.clicked.connect(onFavoriteClick)

    def onCommunityClick():
      enableAll()
      self.ui.btnModelCommunity.setEnabled(False)

    self.ui.btnModelCommunity.clicked.connect(onCommunityClick)

    self.ui.btnSearch.clicked.connect(self.onModelSearchClicked)

  def onModelSearchClicked(self):
    if self.searchThread is not None and self.searchThread.isRunning():
      return

    self._clearResults()

    def run(q):
      models = self.search()
      for model in models: self.sigAddModelResultItem.emit(model)

    self.searchThread = GeneralThread(run)
    self.searchThread.start()

  def search(self):
    args = {
      "query": f"""%{self.ui.inSearchQuery.text()}%""",
    }

    if not self.ui.btnModelPlattform.isEnabled(): args.update({ "official": True })
    elif not self.ui.btnModelYour.isEnabled(): args.update({ "own": True })
    elif not self.ui.btnModelFavorite.isEnabled(): args.update({ "favorites": True })
    elif not self.ui.btnModelCommunity.isEnabled(): args.update({ "official": False })

    if self.ui.cmbOrder.currentIndex() == 0: args.update({ "orderByCreatedAsc": False })
    elif self.ui.cmbOrder.currentIndex() == 1: args.update({ "orderByCreatedAsc": True })
    elif self.ui.cmbOrder.currentIndex() == 2: args.update({ "orderByNameAsc": True })
    elif self.ui.cmbOrder.currentIndex() == 3: args.update({ "orderByNameAsc": False })

    if self.ui.cmbCategory.currentIndex() != 0: args.update({ "category": self.ui.cmbCategory.currentText().replace(" ", "_").upper() })

    return self.getLeonardoAI().getModels(**args)

  def _clearResults(self):
    while self.ui.frmResults.layout().count():
      item = self.ui.frmResults.layout().takeAt(0)
      widget = item.widget()
      if widget: widget.deleteLater()

  @QtCore.pyqtSlot(Model)
  def _addResultItem(self, model: Model):
    item = ModelSearchItem(model)
    item.setDoubleClickListener(self.onModelSelected)

    c = self.ui.frmResults.layout().count()
    self.ui.frmResults.layout().addWidget(item, c // 2, c % 2)

  def onModelSelected(self, model: Model):
    self.choseModelCallback(model)
    self.setVisible(False)