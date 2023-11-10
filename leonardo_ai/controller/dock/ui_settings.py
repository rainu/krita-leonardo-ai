from PyQt5 import QtWidgets

from ...view.settings import Ui_Settings
from ...config import Config, ConfigRegistry
from ...client.graphql.graphql import GraphqlClient
from ...client.restClient import RestClient

class Settings(QtWidgets.QFrame):

  def __init__(self, applyClb: callable):
    super().__init__()
    self.config = Config.instance()

    self.setWindowTitle("Leonardo AI - Settings")

    self.ui = Ui_Settings()
    self.ui.setupUi(self)
    self.applyCallback = applyClb

    def onClientClick():
      self.ui.grpClientGQL.setVisible(self.ui.radClientGQL.isChecked())
      self.ui.grpClientRest.setVisible(self.ui.radClientREST.isChecked())

    self.ui.radClientGQL.clicked.connect(onClientClick)
    self.ui.radClientREST.clicked.connect(onClientClick)

    self.ui.radClientGQL.setChecked(self.config.get(ConfigRegistry.LEONARDO_CLIENT_TYPE) == "gql")
    onClientClick()

    self.ui.inClientUsername.setText(self.config.get(ConfigRegistry.LEONARDO_CLIENT_GQL_USERNAME))
    self.ui.inClientPassword.setText(self.config.get(ConfigRegistry.LEONARDO_CLIENT_GQL_PASSWORD))
    self.ui.inClientKey.setText(self.config.get(ConfigRegistry.LEONARDO_CLIENT_REST_KEY))

    self.ui.chkNSFW.setChecked(self.config.get(ConfigRegistry.GENERAL_NSFW, False))
    self.ui.chkPublic.setChecked(self.config.get(ConfigRegistry.GENERAL_PUBLIC, True))

    self.ui.btnTestGQL.clicked.connect(self.onTestGql)
    self.ui.btnTestREST.clicked.connect(self.onTestRest)
    self.ui.btnClose.clicked.connect(self.onClose)
    self.ui.btnApply.clicked.connect(self.onApply)

  @property
  def nsfw(self):
    return self.ui.chkNSFW.isChecked()

  @property
  def public(self):
    return self.ui.chkPublic.isChecked()

  def onTestGql(self):
    self.ui.lblTestGQL.setText("")

    try:
      if GraphqlClient(self.ui.inClientUsername.text(), self.ui.inClientPassword.text()).getUserInfo().Id is not None:
        self.ui.lblTestGQL.setText("Successful")
        return
    except Exception:
      pass

    self.ui.lblTestGQL.setText("Unsuccessful")


  def onTestRest(self):
    self.ui.lblTestREST.setText("")

    try:
      if RestClient(self.ui.inClientKey.text()).getUserInfo().Id is not None:
        self.ui.lblTestREST.setText("Successful")
        return
    except Exception:
      pass

    self.ui.lblTestREST.setText("Unsuccessful")

  def onApply(self):
    self.config.set(ConfigRegistry.LEONARDO_CLIENT_TYPE, "gql" if self.ui.radClientGQL.isChecked() else "rest")
    self.config.set(ConfigRegistry.LEONARDO_CLIENT_GQL_USERNAME, self.ui.inClientUsername.text())
    self.config.set(ConfigRegistry.LEONARDO_CLIENT_GQL_PASSWORD, self.ui.inClientPassword.text())
    self.config.set(ConfigRegistry.LEONARDO_CLIENT_REST_KEY, self.ui.inClientKey.text())
    self.config.set(ConfigRegistry.GENERAL_NSFW, self.nsfw)
    self.config.set(ConfigRegistry.GENERAL_PUBLIC, self.public)

    self.config.save()
    self.applyCallback()

    self.setVisible(False)

  def onClose(self):
    self.setVisible(False)