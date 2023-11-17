from abc import abstractmethod
from dataclasses import dataclass
from typing import List
from enum import Enum
from datetime import datetime
from PyQt5.QtGui import QImage


@dataclass
class TokenBalance:
  GPT: int
  Model: int
  General: int
  Paid: int

@dataclass
class UserInfo:
  Id: str
  Name: str
  Token: TokenBalance | None = None

class JobStatus(str, Enum):
  PENDING = 'PENDING'
  COMPLETE = 'COMPLETE'
  FAILED = 'FAILED'

class TransformationType(str, Enum):
  UPSCALE = 'UPSCALE'
  UNZOOM = 'UNZOOM'
  NO_BACKGROUND = 'NOBG'

class UpscaleType(str, Enum):
  ALCHEMY_REFINER = 'ALCHEMY_REFINER'
  ALTERNATIVE = 'ALTERNATIVE'
  DEFAULT = 'DEFAULT'
  SMOOTH = 'SMOOTH'
  HD = 'HD'

@dataclass
class AlchemyRefinerSettings:
  Creative: bool
  Strength: float

@dataclass
class ImageVariation:
  Id: str
  Url: str
  Status: JobStatus
  TransformationType: TransformationType
  UpscaleType: UpscaleType = None
  AlchemyRefinerSettings: AlchemyRefinerSettings = None

@dataclass
class Image:
  Id: str
  Url: str
  Creator: UserInfo
  LikeCount: int | None = None
  Variations: list[ImageVariation] | None = None

class PoseToImageType(str, Enum):
  POSE_TO_IMAGE = 'POSE'
  EDGE_TO_IMAGE = 'CANNY'
  DEPTH_TO_IMAGE = 'DEPTH'
  PATTERN_TO_IMAGE = 'QR'

@dataclass
class Model:
  Id: str
  Name: str
  Description: str
  NotSafeForWork: bool
  Public: bool
  Height: int
  Width: int
  PreviewImage: Image | None
  User: UserInfo
  TrainingStrength: str
  StableDiffusionVersion: str

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
  CustomModel: Model | None
  Public: bool
  NotSafeForWork: bool

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
                ids: List[str] | None = None,
                official: bool | None = None,
                complete: bool | None = None,
                favorites: bool | None = None,
                own: bool | None = None,
                category: str | None = None,
                notSafeForWork: bool | None = None,
                orderByCreatedAsc: bool | None = None,
                orderByNameAsc: bool | None = None,
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
  def getGenerations(self,
                     community: bool = False,
                     prompt: str | None = None,
                     negativePrompt: str | None = None,
                     modelIds: list[str] | None = None,
                     minImageHeight: int | None = None,
                     maxImageHeight: int | None = None,
                     minImageWidth: int | None = None,
                     maxImageWidth: int | None = None,
                     notSafeForWork: bool | None = None,
                     minCreatedAt: datetime | None = None,
                     maxCreatedAt: datetime | None = None,
                     status: JobStatus | None = None,
                     orderByCreatedAsc: bool | None = None,
                     offset: int = 0,
                     limit: int = 50) -> List[Generation]:
    pass

  @abstractmethod
  def deleteGenerationById(self, generationId: str) -> None:
    pass

  @abstractmethod
  def removeImageBackground(self, imageId: str) -> str:
    pass

  @abstractmethod
  def removeImageVariationBackground(self, variationId: str) -> str:
    pass

  @abstractmethod
  def unzoomImage(self, imageId: str) -> str:
    pass

  @abstractmethod
  def unzoomImageVariation(self, imageVariationId: str) -> str:
    pass

  @abstractmethod
  def upscaleImage(self, imageId: str, upscaleType: UpscaleType, alchemyRefinerSettings: AlchemyRefinerSettings | None = None) -> str:
    pass

  @abstractmethod
  def upscaleImageVariation(self, imageVariationId: str, upscaleType: UpscaleType, alchemyRefinerSettings: AlchemyRefinerSettings | None = None) -> str:
    pass

  @abstractmethod
  def createImageGeneration(self,
                            prompt: str,
                            width: int,
                            height: int,
                            negativePrompt: str = "",
                            notSafeForWork: bool = True,
                            numberOfImages: int = 4,
                            inferenceSteps: int = 10,
                            guidanceScale: int = 7,
                            photoRealStrength: float | None = None,
                            photoRealHighContrast: bool = False,
                            photoRealStyle: str = "CINEMATIC",
                            promptMagicStrength: float | None = None,
                            promptMagicHighContrast: bool | None = None,
                            promptMagicVersion: str = "v2",
                            alchemyHighResolution: bool | None = None,
                            alchemyContrastBoost: float | None = None,
                            alchemyResonance: int | None = None,
                            tiling: bool = False,
                            sdVersion: str = "v1_5",
                            modelId: str | None = None,
                            presetStyle: str | None = None,
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
                              notSafeForWork: bool = True,
                              numberOfImages: int = 4,
                              inferenceSteps: int = 10,
                              guidanceScale: int = 7,
                              sdVersion: str = "v1_5",
                              modelId: str | None = None,
                              presetStyle: str | None = None,
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
                                  notSafeForWork: bool = True,
                                  numberOfImages: int = 4,
                                  inferenceSteps: int = 10,
                                  guidanceScale: int = 7,
                                  sdVersion: str = "v1_5",
                                  modelId: str | None = None,
                                  presetStyle: str | None = None,
                                  poseToImage: PoseToImageType | None = None,
                                  controlnetWeight: float = 0.75,
                                  tiling: bool = False,
                                  alchemyHighResolution: bool | None = None,
                                  alchemyContrastBoost: float | None = None,
                                  alchemyResonance: int | None = None,
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
                                   notSafeForWork: bool = True,
                                   numberOfImages: int = 4,
                                   inferenceSteps: int = 10,
                                   guidanceScale: int = 7,
                                   sdVersion: str = "v1_5",
                                   modelId: str | None = None,
                                   presetStyle: str | None = None,
                                   scheduler: str = "LEONARDO",
                                   public: bool = False,
                                   imageStrength: float = 0.1,
                                   seed: int | None = None,
                                   ) -> str:
    pass
