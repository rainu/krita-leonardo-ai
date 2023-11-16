import os
import hashlib
import tempfile

from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPixmap

from ..config import Config, ConfigRegistry

class ImageCache(QObject):
  __instance = None
  sigImageSave = QtCore.pyqtSignal(str, bytes)

  def __init__(self):
    QObject.__init__(self)
    self.sigImageSave.connect(self.save)

  @classmethod
  def instance(cls):
    if cls.__instance is None:
      cls.__instance = ImageCache()

    return cls.__instance

  def exists(self, imageUrl: str):
    return os.path.isfile(self.path(imageUrl))

  def load(self, imageUrl: str) -> QPixmap:
    return QPixmap(self.path(imageUrl))

  @QtCore.pyqtSlot(str, bytes)
  def save(self, imageUrl: str, imageContent: bytes):
    with open(self.path(imageUrl), 'wb') as imageFile:
      imageFile.write(imageContent)

  def path(self, imageUrl: str) -> str:
    return os.path.join(
      Config.instance().get(ConfigRegistry.IMAGE_CACHE_DIRECTORY, tempfile.gettempdir()),
      self.toId(imageUrl),
    ) + ".png"

  def toId(self, imageUrl: str) -> str:
    return hashlib.md5(imageUrl.encode()).hexdigest()
