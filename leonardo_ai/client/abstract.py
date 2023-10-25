from abc import abstractmethod
from dataclasses import dataclass
from typing import List
from enum import Enum
from datetime import datetime
from PyQt5.QtGui import QImage


@dataclass
class UserInfo:
  Id: str
  Name: str


@dataclass
class Image:
  Id: str
  Url: str


class JobStatus(str, Enum):
  PENDING = 'PENDING'
  COMPLETE = 'COMPLETE'
  FAILED = 'FAILED'


class PoseToImageType(str, Enum):
  POSE_TO_IMAGE = 'POSE'
  EDGE_TO_IMAGE = 'CANNY'
  DEPTH_TO_IMAGE = 'DEPTH'
  PATTERN_TO_IMAGE = 'QR'


@dataclass
class Generation:
  Id: str
  CreatedAt: datetime
  GeneratedImages: List[Image]
  ImageHeight: int
  ImageWidth: int
  Seed: int
  Status: JobStatus
  Prompt: str
  NegativePrompt: str
  SDVersion: str

@dataclass
class Model:
  Id: str
  Name: str
  Description: str
  NotSaveForWork: bool
  Public: bool
  Height: int
  Width: int
  PreviewImage: Image | None
  User: UserInfo
  TrainingStrength: str
  StableDiffusionVersion: str

@dataclass
class Element:
  Id: str
  Name: str
  Description: str
  PreviewImageUrl: str
  BaseModel: str
  WeightDefault: float
  WeightMin: float
  WeightMax: float

class AbstractClient:
  @abstractmethod
  def getUserInfo(self) -> UserInfo | None:
    pass

  @abstractmethod
  def getModels(self,
                query: str = "%%",
                official: bool | None = None,
                complete: bool | None = None,
                notSaveForWork: bool | None = None,
                offset: int = 0,
                limit: int = 50) -> List[Model]:
    pass

  @abstractmethod
  def getElements(self, query: str = "%%", baseModel: str | None = None, offset: int = 0, limit: int = 64) -> List[Element]:
    pass

  @abstractmethod
  def getGenerationById(self, generationId: str) -> Generation | None:
    pass

  @abstractmethod
  def createImageGeneration(self,
                            prompt: str,
                            width: int,
                            height: int,
                            negativePrompt: str = "",
                            notSaveForWork: bool = True,
                            numberOfImages: int = 4,
                            inferenceSteps: int = 10,
                            guidanceScale: int = 7,
                            photoRealStrength: float | None = None,
                            photoRealContrastRatio: float | None = None,
                            photoRealStyle: str | None = None,
                            promptMagicStrength: float | None = None,
                            promptMagicHighContrast: bool | None = None,
                            useAlchemy: bool = False,
                            tiling: bool = False,
                            sdVersion: str = "v1_5",
                            modelId: str | None = None,
                            scheduler: str = "LEONARDO",
                            public: bool = False,
                            seed: int | None = None,
                            ) -> str:
    pass

  @abstractmethod
  def createInpaintGeneration(self,
                              prompt: str,
                              image: QImage,
                              mask: QImage | None = None,
                              negativePrompt: str = "",
                              notSaveForWork: bool = True,
                              numberOfImages: int = 4,
                              inferenceSteps: int = 10,
                              guidanceScale: int = 7,
                              sdVersion: str = "v1_5",
                              modelId: str | None = None,
                              scheduler: str = "LEONARDO",
                              public: bool = False,
                              imageStrength: float = 0.0,
                              seed: int | None = None,
                              ) -> str:
    pass

  @abstractmethod
  def createImage2ImageGeneration(self,
                                  prompt: str,
                                  image: QImage,
                                  negativePrompt: str = "",
                                  notSaveForWork: bool = True,
                                  useAlchemy: bool = False,
                                  numberOfImages: int = 4,
                                  inferenceSteps: int = 10,
                                  guidanceScale: int = 7,
                                  sdVersion: str = "v1_5",
                                  modelId: str | None = None,
                                  poseToImage: PoseToImageType | None = None,
                                  controlnetWeight: float = 0.75,
                                  tiling: bool = False,
                                  scheduler: str = "LEONARDO",
                                  public: bool = False,
                                  imageStrength: float = 0.1,
                                  seed: int | None = None,
                                  ) -> str:
    pass

  @abstractmethod
  def createSketch2ImageGeneration(self,
                                   prompt: str,
                                   image: QImage,
                                   mask: QImage | None = None,
                                   negativePrompt: str = "",
                                   notSaveForWork: bool = True,
                                   numberOfImages: int = 4,
                                   inferenceSteps: int = 10,
                                   guidanceScale: int = 7,
                                   sdVersion: str = "v1_5",
                                   modelId: str | None = None,
                                   scheduler: str = "LEONARDO",
                                   public: bool = False,
                                   imageStrength: float = 0.1,
                                   seed: int | None = None,
                                   ) -> str:
    pass
