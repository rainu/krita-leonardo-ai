from .ui_image2image import Image2Image

class Sketch2Image(Image2Image):

  def __init__(self):
    super().__init__()

    def onOverrideDefaults(): self.ui.grpSketch2ImageDefaults.setVisible(self.ui.chkOverrideDefaults.isChecked())
    self.ui.chkOverrideDefaults.stateChanged.connect(onOverrideDefaults)
    onOverrideDefaults()

    def onInputStrengthChange(): self.ui.lblSketch2ImageStrength.setText(str(self.inputStrength))
    self.ui.slSketch2ImageStrength.valueChanged.connect(onInputStrengthChange)

  @property
  def inputStrength(self):
    return self.ui.slSketch2ImageStrength.value() / 100