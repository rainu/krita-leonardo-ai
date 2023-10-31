from krita import DockWidget

from ...view.dock import Ui_LeonardoAI

class BaseDock(DockWidget):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("Leonardo AI")

    self.ui = Ui_LeonardoAI()
    self.ui.setupUi(self)

    self.ui.inPrompt.textChanged.connect(self.onPromptChange)

    self.ui.tabType.currentChanged.connect(self.onTabChange)

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

  def onPromptChange(self):
    self.ui.btnGenerate.setEnabled(self.prompt != "")

  def onTabChange(self):
    if self.ui.tabType.currentIndex() == 0: self.onTabText2ImageActivate()
    elif self.ui.tabType.currentIndex() == 1: self.onTabInpaintActivate()
    elif self.ui.tabType.currentIndex() == 2: self.onTabOutpaintActivate()
    elif self.ui.tabType.currentIndex() == 3: self.onTabImage2ImageActivate()
    elif self.ui.tabType.currentIndex() == 4: self.onTabSketch2ImageActivate()


  def onTabText2ImageActivate(self): pass
  def onTabInpaintActivate(self): pass
  def onTabOutpaintActivate(self): pass
  def onTabImage2ImageActivate(self): pass
  def onTabSketch2ImageActivate(self): pass
