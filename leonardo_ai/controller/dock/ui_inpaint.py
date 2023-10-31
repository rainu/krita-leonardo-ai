from .ui_text2image import Text2Image

class Inpaint(Text2Image):

  def __init__(self):
    super().__init__()

    def onStrengthChange(): self.ui.lblInpaintStrength.setText(str(self.inpaintStrength))
    self.ui.slInpaintStrength.valueChanged.connect(onStrengthChange)

  @property
  def inpaintStrength(self):
    return self.ui.slInpaintStrength.value() / 100