import inspect
import traceback
from typing import Callable

from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot
from PyQt5.QtGui import QPixmap
from requests import Request, Response, Session

class __globalThreadPool__:
  __instance: QThreadPool = None

  def __init__(self):
    raise RuntimeError('Call instance() instead')

  @classmethod
  def instance(cls) -> QThreadPool:
    if cls.__instance is None:
      cls.__instance = QThreadPool()

    return cls.__instance

class __imageThreadPool__:
  __instance: QThreadPool = None

  def __init__(self):
    raise RuntimeError('Call instance() instead')

  @classmethod
  def instance(cls) -> QThreadPool:
    if cls.__instance is None:
      cls.__instance = QThreadPool()

    return cls.__instance

class GeneralThread(QRunnable):
  def __init__(self, target: Callable[[any], any], signalDone = None, signalError = None, metaData = None):
    QRunnable.__init__(self)

    self.sigInt = False
    self.running = False
    self.target = target
    self.signalDone = signalDone
    self.signalError = signalError
    self.metaData = metaData

  def __getThreadPool__(self) -> QThreadPool:
    return __globalThreadPool__.instance()

  @property
  def hasReturnDefined(self):
    sig = inspect.signature(self.target)
    return sig.return_annotation != inspect.Signature.empty if sig else False

  def requestInterruption(self):
    self.sigInt = True

  def isInterruptionRequested(self):
    return self.sigInt

  def isRunning(self):
    return self.running

  def terminate(self):
    try:
      self.__getThreadPool__().tryTake(self)
    except: pass

    self.sigInt = True
    self.signalDone = None
    self.signalError = None

  @pyqtSlot()
  def run(self):
    self.running = True

    try:
      result = self.target(self)

      if self.hasReturnDefined: self._emitSignal(result)
    except Exception as e:
      self._onException(e)
    finally:
      self.running = False

  def start(self):
    self.sigInt = False
    self.__getThreadPool__().start(self)

  def _emitSignal(self, data):
    if self.signalDone is not None:
      if self.metaData is None: self.signalDone.emit(data)
      else: self.signalDone.emit(data, self.metaData)

  def _onException(self, e: Exception):
    print("Error while executing thread!")
    traceback.print_exc()

    if self.signalError is not None:
      self.signalError.emit(e)

class RequestThread(GeneralThread):
  def __init__(self, request: Request, signalResponse, signalError = None, metaData = None):
    GeneralThread.__init__(self, self._run, signalResponse, signalError, metaData)

    self.request = request.prepare()

  def _run(self, t: QRunnable):
    try:
      self._onResponse(Session().send(self.request))
    except Exception as e:
      print("Unable to load image: ", e)
      self._onException(e)

  def _onResponse(self, response: Response):
    self._emitSignal(response)

class GetRequestThread(RequestThread):

  def __init__(self, url: str, signalDone, signalError = None, metaData = None):
    RequestThread.__init__(self, Request("GET", url), signalDone, signalError, metaData)

class ImageRequestThread(GetRequestThread):

  def __init__(self, url: str, signalDone, signalError = None, metaData = None):
    GetRequestThread.__init__(self, url, signalDone, signalError, metaData)

  def __getThreadPool__(self) -> QThreadPool:
    return __imageThreadPool__.instance()

  def _onResponse(self, response: Response):
    if response.status_code != 200:
      self._onException(Exception(f"""received invalid status code: {response.status_code}"""))
      return

    data = response.content
    pixmap = QPixmap()
    pixmap.loadFromData(data)

    try:
      self._emitSignal(pixmap)
    except Exception as e:
      traceback.print_exc()
