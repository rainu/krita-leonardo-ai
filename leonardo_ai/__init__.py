from .dependency import checkPipLib

checkPipLib([
  {"leonardoaisdk": "Leonardo-Ai-SDK"},
])

from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita
from .docker import *

Krita.instance().addDockWidgetFactory(
  DockWidgetFactory(
    "leonardo_ai_docker",
    DockWidgetFactoryBase.DockRight,
    LeonardoAIDocker
  )
)
