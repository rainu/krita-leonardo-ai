from .ui_outpaint import Outpaint

class Image2Image(Outpaint):

  def __init__(self):
    super().__init__()

    def onStrengthChange(): self.ui.lblImageStrength.setText(str(self.imageStrength))
    self.ui.slImageStrength.valueChanged.connect(onStrengthChange)

    def onControlNetChange():
      self.ui.grpControlNet.setVisible(self.controlNet)
      if self.controlNet: self.ui.chkI2IAlchemy.setChecked(False)

    self.ui.chkControlNet.stateChanged.connect(onControlNetChange)
    onControlNetChange()

    def onWeightChange(): self.ui.lblControlNetWeight.setText(str(self.controlNetWeight))
    self.ui.slControlNetWeight.valueChanged.connect(onWeightChange)

    def onAlchemyChange():
      self.ui.grpI2IAlchemy.setVisible(self.ui.chkI2IAlchemy.isChecked())
      if self.ui.chkI2IAlchemy.isChecked():
        self.ui.chkControlNet.setChecked(False)

    self.ui.chkI2IAlchemy.stateChanged.connect(onAlchemyChange)
    onAlchemyChange()

    def onContrastBoostChange(): self.ui.lblI2IAlchemyContrastBoost.setText(str(self.alchemyI2IContrastBoost))
    self.ui.slI2IAlchemyContrastBoost.valueChanged.connect(onContrastBoostChange)

    def onResonanceChange(): self.ui.lblI2IAlchemyResonance.setText(str(self.alchemyI2IResonance))
    self.ui.slI2IAlchemyResonance.valueChanged.connect(onResonanceChange)

  def onTabImage2ImageActivate(self):
    self.ui.conImage2ImageAlchemy.layout().addWidget(self.ui.frmAlchemy)

  @property
  def imageStrength(self):
    return self.ui.slImageStrength.value() / 100

  @property
  def tiling(self):
    return self.ui.chkTiling.isChecked()

  @property
  def controlNet(self):
    return self.ui.chkControlNet.isChecked()

  @property
  def controlNetType(self):
    if self.ui.cmbControlNet.currentIndex() == 0: return "POSE"
    if self.ui.cmbControlNet.currentIndex() == 1: return "CANNY"
    if self.ui.cmbControlNet.currentIndex() == 2: return "DEPTH"
    if self.ui.cmbControlNet.currentIndex() == 3: return "QR"
    return None

  @property
  def controlNetWeight(self):
    return self.ui.slControlNetWeight.value() / 100

  @property
  def alchemyI2IHighResolution(self):
    return self.ui.chkI2IAlchemyHighResolution.isChecked()

  @property
  def alchemyI2IContrastBoost(self):
    return self.ui.slI2IAlchemyContrastBoost.value() / 100

  @property
  def alchemyI2IResonance(self):
    return self.ui.slI2IAlchemyResonance.value()