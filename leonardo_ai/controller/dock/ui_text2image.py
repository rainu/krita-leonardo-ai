import re

from .ui_advanced import AdvancedSettings

class Text2Image(AdvancedSettings):

  def __init__(self):
    super().__init__()

    self._dimButtonPattern = r'^btnDim([0-9]+)x([0-9]+)$'
    for key, value in self.ui.__dict__.items():
      if re.fullmatch(self._dimButtonPattern, key):
        value.clicked.connect(self.onChangeDimension)

    def onSlDimWidthChange(): self.ui.inDimWidth.setValue(self.ui.slDimWidth.value())
    def onInDimWidthChange(): self.ui.slDimWidth.setValue(self.ui.inDimWidth.value())
    self.ui.slDimWidth.valueChanged.connect(onSlDimWidthChange)
    self.ui.inDimWidth.valueChanged.connect(onInDimWidthChange)

    def onSlDimHeightChange(): self.ui.inDimHeight.setValue(self.ui.slDimHeight.value())
    def onInDimHeightChange(): self.ui.slDimHeight.setValue(self.ui.inDimHeight.value())
    self.ui.slDimHeight.valueChanged.connect(onSlDimHeightChange)
    self.ui.inDimHeight.valueChanged.connect(onInDimHeightChange)

    def onDimSwap(): w = self.ui.inDimWidth.value(); self.ui.inDimWidth.setValue(self.ui.inDimHeight.value()); self.ui.inDimHeight.setValue(w)
    self.ui.btnDimSwap.clicked.connect(onDimSwap)

    def onPhotoRealChanged():
      self.ui.grpPhotoReal.setVisible(self.ui.chkPhotoReal.isChecked())
      if self.ui.chkPhotoReal.isChecked():
        self.ui.chkAlchemy.setChecked(True)

    self.ui.chkPhotoReal.stateChanged.connect(onPhotoRealChanged)
    onPhotoRealChanged()

    self.ui.chkAlchemy.stateChanged.connect(self.onAlchemyChange)
    self.onAlchemyChange()

    def onContrastBoostChange(): self.ui.lblAlchemyContrastBoost.setText(str(self.alchemyContrastBoost))
    self.ui.slAlchemyContrastBoost.valueChanged.connect(onContrastBoostChange)

    def onResonanceChange(): self.ui.lblAlchemyResonance.setText(str(self.alchemyResonance))
    self.ui.slAlchemyResonance.valueChanged.connect(onResonanceChange)

    def onPromptMagicChange():
      self.ui.grpAlchemyPromptMagicV2.setVisible(self.ui.radAlchemyPromptMagicV2.isChecked())
      self.ui.grpAlchemyPromptMagicV3.setVisible(self.ui.radAlchemyPromptMagicV3.isChecked())

    self.ui.buttonGroup.buttonToggled.connect(onPromptMagicChange)
    onPromptMagicChange()

    def onMagicPromptV2StrengthChange(): self.ui.lblAlchemyPromptMagicStrengthV2.setText(str(self.alchemyPromptMagicV2Strength))
    self.ui.slAlchemyPromptMagicStrengthV2.valueChanged.connect(onMagicPromptV2StrengthChange)

    def onMagicPromptV3StrengthChange(): self.ui.lblAlchemyPromptMagicStrengthV3.setText(str(self.alchemyPromptMagicV3Strength))
    self.ui.slAlchemyPromptMagicStrengthV3.valueChanged.connect(onMagicPromptV3StrengthChange)

  def onChangeDimension(self):
    width, height = re.search(self._dimButtonPattern, self.sender().objectName()).groups()
    width = int(width)
    height = int(height)

    self.ui.inDimWidth.setValue(width)
    self.ui.inDimHeight.setValue(height)
    self.ui.slDimWidth.setValue(width)
    self.ui.slDimHeight.setValue(height)

  def onTabText2ImageActivate(self):
    self.ui.conText2ImageAlchemy.layout().addWidget(self.ui.frmAlchemy)

  def onAlchemyChange(self):
    self.ui.grpAlchemy.setVisible(self.ui.chkAlchemy.isChecked())
    if not self.ui.chkAlchemy.isChecked():
      self.ui.chkPhotoReal.setChecked(False)

  @property
  def dimWidth(self):
      return int(self.ui.inDimWidth.text())

  @property
  def dimHeight(self):
      return int(self.ui.inDimHeight.text())

  @property
  def photoRealStyle(self):
    if self.ui.chkPhotoReal.isChecked():
      return self.ui.cmbPhotoRealStyle.currentText().upper()

    return None

  @property
  def photoRealDepthOfField(self):
    return self.ui.cmbPhotoRealDepthOfField.currentText().upper()

  @property
  def photoRealStrength(self):
    if self.ui.chkPhotoReal.isChecked():
      if self.photoRealDepthOfField == "HIGH": return 0.45
      if self.photoRealDepthOfField == "MEDIUM": return 0.5
      if self.photoRealDepthOfField == "LOW": return 0.55

    return None

  @property
  def photoRealRawMode(self):
    return self.ui.chkPhotoRealRawMode.isChecked()

  @property
  def alchemyHighResolution(self):
    return self.ui.chkAlchemyHighResolution.isChecked()

  @property
  def alchemyContrastBoost(self):
    return self.ui.slAlchemyContrastBoost.value() / 100

  @property
  def alchemyResonance(self):
    return self.ui.slAlchemyResonance.value()

  @property
  def alchemyPromptMagicVersion(self):
    if self.ui.radAlchemyPromptMagicV2.isChecked(): return "V2"
    if self.ui.radAlchemyPromptMagicV3.isChecked(): return "V3"
    return None

  @property
  def alchemyPromptMagicStrength(self):
    if self.ui.radAlchemyPromptMagicV2.isChecked(): return self.alchemyPromptMagicV2Strength
    if self.ui.radAlchemyPromptMagicV3.isChecked(): return self.alchemyPromptMagicV3Strength
    return None

  @property
  def alchemyHighContrast(self):
    if self.ui.radAlchemyPromptMagicV2.isChecked(): return self.ui.chkAlchemyHighContrast.isChecked()
    if self.ui.radAlchemyPromptMagicV3.isChecked(): return not self.ui.chkAlchemyRawMode.isChecked()
    return None

  @property
  def alchemyPromptMagicV2Strength(self):
    return self.ui.slAlchemyPromptMagicStrengthV2.value() / 100

  @property
  def alchemyPromptMagicV3Strength(self):
    return self.ui.slAlchemyPromptMagicStrengthV3.value() / 100

  @property
  def t2iTiling(self):
    return self.ui.chkText2ImageTiling.isChecked()