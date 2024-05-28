from .dependencies import installDependencies

installDependencies()

from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita

from .controller.dock.leonardo import LeonardoDock

Krita.instance().addDockWidgetFactory(
  DockWidgetFactory(
    "leonardo_ai_docker",
    DockWidgetFactoryBase.DockRight,
    LeonardoDock
  )
)
