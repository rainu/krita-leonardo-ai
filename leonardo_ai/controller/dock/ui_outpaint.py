from krita import Selection

from .ui_inpaint import Inpaint

class Outpaint(Inpaint):

  def __init__(self):
    super().__init__()

    def onInsertSelectionLeft():
        s = Selection()
        s.select(-self.model.Width + self.selectionPadding, 0, self.model.Width, self.model.Height, 255)
        Krita.instance().activeDocument().setSelection(s)

    def onInsertSelectionTop():
        s = Selection()
        s.select(0, -self.model.Height + self.selectionPadding, self.model.Width, self.model.Height, 255)
        Krita.instance().activeDocument().setSelection(s)

    def onInsertSelectionRight():
        doc = Krita.instance().activeDocument()
        s = Selection()
        s.select(doc.width() - self.selectionPadding, 0, self.model.Width, self.model.Height, 255)
        doc.setSelection(s)

    def onInsertSelectionBottom():
      doc = Krita.instance().activeDocument()
      s = Selection()
      s.select(0, doc.height() - self.selectionPadding, self.model.Width, self.model.Height, 255)
      doc.setSelection(s)

    self.ui.btnOutpaintInsertSelectionLeft.clicked.connect(onInsertSelectionLeft)
    self.ui.btnOutpaintInsertSelectionTop.clicked.connect(onInsertSelectionTop)
    self.ui.btnOutpaintInsertSelectionRight.clicked.connect(onInsertSelectionRight)
    self.ui.btnOutpaintInsertSelectionBottom.clicked.connect(onInsertSelectionBottom)

  def onModelSelect(self):
    super().onModelSelect()

    self.ui.btnOutpaintInsertSelectionLeft.setEnabled(self.model is not None)
    self.ui.btnOutpaintInsertSelectionTop.setEnabled(self.model is not None)
    self.ui.btnOutpaintInsertSelectionRight.setEnabled(self.model is not None)
    self.ui.btnOutpaintInsertSelectionBottom.setEnabled(self.model is not None)
    self.ui.inOutpaintInsertSelectionPadding.setEnabled(self.model is not None)


  @property
  def selectionPadding(self) -> int:
    return self.ui.inOutpaintInsertSelectionPadding.value()