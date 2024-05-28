import os
import shutil
import sys
import tarfile
from pathlib import Path
from urllib.request import urlretrieve

PACKAGE_DIR = Path(os.path.realpath(__file__)).parent / "packages"
PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
sys.path.append(PACKAGE_DIR.as_posix())

class Dependency:
  def __init__(self, name: str, url: str, sourceDir: str | None = None):
    self.name = name
    self.url = url

    if sourceDir is None:
      self.sourceDir = Path("src") / name
    else:
      self.sourceDir = sourceDir

  def install(self) -> None:
    fileName = self.url.split("/")[-1]
    fileDestination = PACKAGE_DIR / fileName
    target = PACKAGE_DIR / self.name

    if not fileDestination.exists():
      print("\tDownloading...")
      urlretrieve(self.url, fileDestination)

    if not target.exists():
      with tarfile.open(fileDestination) as tar:
        print("\tExtracting...")
        tar.extractall(PACKAGE_DIR)

      unpacked = PACKAGE_DIR / fileName.replace(".tar", "").replace(".gz", "")
      unpackedSourceDir = unpacked / self.sourceDir
      unpackedSourceDir.rename(target)

      # check if there is an __init__.py file included
      if not (target / "__init__.py").exists():
        print("\tModify...")
        shutil.copyfile(target / (self.name + ".py"), target / "__init__.py")

      if unpacked.exists():
        print("\tCleanup...")
        shutil.rmtree(unpacked)

DEPENDENCIES = [
  Dependency("requests", "https://files.pythonhosted.org/packages/86/ec/535bf6f9bd280de6a4637526602a146a68fde757100ecf8c9333173392db/requests-2.32.2.tar.gz"),
    Dependency("urllib3", "https://files.pythonhosted.org/packages/7a/50/7fd50a27caa0652cd4caf224aa87741ea41d3265ad13f010886167cfcc79/urllib3-2.2.1.tar.gz"),
    Dependency("idna", "https://files.pythonhosted.org/packages/21/ed/f86a79a07470cb07819390452f178b3bef1d375f2ec021ecfc709fc7cf07/idna-3.7.tar.gz", "idna"),
    Dependency("certifi", "https://files.pythonhosted.org/packages/71/da/e94e26401b62acd6d91df2b52954aceb7f561743aa5ccc32152886c76c96/certifi-2024.2.2.tar.gz", "certifi"),
    Dependency("charset_normalizer", "https://files.pythonhosted.org/packages/63/09/c1bc53dab74b1816a00d8d030de5bf98f724c52c1635e07681d312f20be8/charset-normalizer-3.3.2.tar.gz", "charset_normalizer"),
  Dependency("leonardoaisdk", "https://files.pythonhosted.org/packages/cb/54/3463d7d7af8424e30d3f85cbcca04b811db64f489e1f221cb98e52846d8a/Leonardo-Ai-SDK-2.0.0.tar.gz"),
    Dependency("dataclasses_json", "https://files.pythonhosted.org/packages/f6/46/7cecfeb3e9419cbdc45f4425446a0fa8d914ceeb2d0c9fe6648f1691d592/dataclasses_json-0.6.6.tar.gz", "dataclasses_json"),
    Dependency("marshmallow", "https://files.pythonhosted.org/packages/a2/16/06ad266adc423f9d7ee49dce26787b973907aa70213760c9fe1711745405/marshmallow-3.21.2.tar.gz"),
    Dependency("mypy_extensions", "https://files.pythonhosted.org/packages/98/a4/1ab47638b92648243faf97a5aeb6ea83059cc3624972ab6b8d2316078d3f/mypy_extensions-1.0.0.tar.gz", ""),
    Dependency("dateutil", "https://files.pythonhosted.org/packages/66/c0/0c8b6ad9f17a802ee498c46e004a0eb49bc148f2fd230864601a86dcf6db/python-dateutil-2.9.0.post0.tar.gz"),
    Dependency("six", "https://files.pythonhosted.org/packages/71/39/171f1c67cd00715f190ba0b100d606d440a28c93c7714febeca8b79af85e/six-1.16.0.tar.gz", ""),
    Dependency("packaging", "https://files.pythonhosted.org/packages/ee/b5/b43a27ac7472e1818c4bafd44430e69605baefe1f34440593e0332ec8b4d/packaging-24.0.tar.gz"),
    Dependency("typing_inspect", "https://files.pythonhosted.org/packages/dc/74/1789779d91f1961fa9438e9a8710cdae6bd138c80d7303996933d117264a/typing_inspect-0.9.0.tar.gz", ""),
    Dependency("typing_extensions", "https://files.pythonhosted.org/packages/ce/6a/aa0a40b0889ec2eb81a02ee0daa6a34c6697a605cf62e6e857eead9e4f85/typing_extensions-4.12.0.tar.gz", "src"),
    Dependency("jsonpath", "https://files.pythonhosted.org/packages/b5/49/e582e50b0c54c1b47e714241c4a4767bf28758bf90212248aea8e1ce8516/jsonpath-python-1.0.6.tar.gz", "jsonpath")
]

def installDependencies() -> None:
  print("Check and Installing dependencies...")
  print("====================================")

  for i, dependency in enumerate(DEPENDENCIES):
    print(f"Check {dependency.name} {i + 1}/{len(DEPENDENCIES)}")
    dependency.install()

  print("====================================")

if __name__ == '__main__':
    installDependencies()