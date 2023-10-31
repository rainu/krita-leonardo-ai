from .ui_general import BaseDock

class AdvancedSettings(BaseDock):

  def __init__(self):
    super().__init__()

    def onGuidanceScaleChange(): self.ui.lblGuidanceScale.setText(str(self.guidanceScale))
    self.ui.slGuidanceScale.valueChanged.connect(onGuidanceScaleChange)

    def onClickAdvancedSettings(): self.ui.grpAdvancedSettings.setVisible(not self.ui.grpAdvancedSettings.isVisible())
    self.ui.btnAdvancedSettings.clicked.connect(onClickAdvancedSettings)
    self.ui.grpAdvancedSettings.setVisible(False)

    def onToggleSeed(): self.ui.inSeed.setVisible(self.ui.chkSeed.isChecked())
    self.ui.chkSeed.clicked.connect(onToggleSeed)
    onToggleSeed()

    def onChangeScheduler():
      self.ui.lblStepCount.setVisible(self.ui.cmbScheduler.currentIndex() != 6)
      self.ui.lblStepCountValue.setVisible(self.ui.cmbScheduler.currentIndex() != 6)
      self.ui.slStepCount.setVisible(self.ui.cmbScheduler.currentIndex() != 6)
    self.ui.cmbScheduler.currentIndexChanged.connect(onChangeScheduler)
    onChangeScheduler()

    def onStepCountChanged(): self.ui.lblStepCountValue.setText(str(self.stepCount))
    self.ui.slStepCount.valueChanged.connect(onStepCountChanged)

  @property
  def guidanceScale(self):
    return self.ui.slGuidanceScale.value()

  @property
  def seed(self):
    if not self.ui.inSeed.isVisible(): return None
    return self.ui.inSeed.text()

  @property
  def scheduler(self):
    value = self.ui.cmbScheduler.currentText()
    value = value.upper()
    value = value.replace(" ", "_")

    if value == "EULER_ANCESTRAL": value = "EULER_ANCESTRAL_DISCRETE"

    return value

  @property
  def stepCount(self):
    if self.ui.slStepCount.isVisible(): return self.ui.slStepCount.value()
    return None