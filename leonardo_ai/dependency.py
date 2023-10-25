# code from: https://krita-artists.org/t/use-of-external-pip-libraries-in-python-plugins/21739

from PyQt5.Qt import *

import sys
import os
import runpy


def pipInstallPath():
  """Return pip lib path

  Eventually:
  - create directory if not exist
  - add it to sys.path
  """
  returned = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), 'pykrita', 'piplib')

  if not os.path.isdir(returned):
    os.makedirs(returned)

  if not returned in sys.path:
    sys.path.append(returned)

  return returned


def pip(param):
  """Execute pip

  Given `param` is a list of pip command line parameters


  Example:
      To execute:
          "python -m pip install numpy"

      Call function:
          pip(["install", "numpy"])
  """

  def exitFct(exitCode):
    return exitCode

  pipLibPath = pipInstallPath()

  # keep pointer to original values
  sysArgv = sys.argv
  sysExit = sys.exit

  # replace exit function to be sure that pip won't stop script
  sys.exit = exitFct

  # prepare arguments for pip module
  sys.argv = ["pip"] + param
  sys.argv.append(f'--target={pipLibPath}')

  # print("pip command:", sys.argv)
  runpy.run_module("pip", run_name='__main__')

  sys.exit = sysExit
  sys.argv = sysArgv


def checkPipLib(libNames):
  """Import a library installed from pip (example: numpy)

  If library doesn't exists, do pip installation
  """
  pipLibPath = pipInstallPath()

  if isinstance(libNames, list) or isinstance(libNames, tuple):
    installList = []
    for libName in libNames:
      if isinstance(libName, dict):
        libNameCheck = list(libName.keys())[0]
        libInstall = libName[libNameCheck]
      elif isinstance(libName, str):
        libNameCheck = libName
        libInstall = libName

      try:
        # try to import module
        print("Try to load", libNameCheck)
        __import__(libNameCheck)
        print("Ok!")
      except Exception as e:
        print("Failed", str(e))
        installList.append(libInstall)

    if len(libInstall) > 0:
      pip(["install"] + installList)
  elif isinstance(libNames, str):
    checkPipLib([libNames])
