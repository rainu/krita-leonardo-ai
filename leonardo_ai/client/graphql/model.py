from dataclasses import dataclass
from typing import List


@dataclass
class uploadImageInfo:
  Id: str
  Key: str
  Url: str
  Fields: dict

  def __init__(self, Id: str, Key: str, Url: str, Fields: dict):
    self.Id = Id
    self.Key = Key
    self.Url = Url
    self.Fields = Fields

@dataclass
class modelParameter:
  Id: str | None
  StableDiffusionVersion: str
  PresetStyle: str = "NONE"

@dataclass
class promptMagicParameter:
  Strength: float
  HighContrast: bool
  Version: str

@dataclass
class photoRealParameter:
  Strength: float
  HighContrast: bool
  Style: str

@dataclass
class alchemyParameter:
  HighResolution: bool
  ContrastBoost: float
  Resonance: int

@dataclass
class canvasParameter:
  InitId: str
  Strength: float
  RequestType: str
  MaskId: str | None = None

@dataclass
class controlNetParameter:
  Type: str
  Weight: float

@dataclass
class elementParameter:
  Id: str
  Weight: float

@dataclass
class generationParameter:
  Prompt: str
  NegativePrompt: str
  Model: modelParameter
  ImageCount: int
  ImageWidth: int
  ImageHeight: int
  InferenceSteps: int
  GuidanceScale: int
  Public: bool
  NotSaveForWork: bool
  LeonardoMagic: bool | None = None
  Tiling: bool | None = None
  Canvas: canvasParameter | None = None
  PromptMagic: promptMagicParameter | None = None
  PhotoReal: photoRealParameter | None = None
  Alchemy: alchemyParameter | None = None
  ControlNet: controlNetParameter | None = None
  Elements: List[elementParameter] = None
  Scheduler: str | None = None
  Seed: int | None = None

  def ToArgs(self) -> dict:
    content = {
      "prompt": self.Prompt,
      "negative_prompt": self.NegativePrompt,
      "nsfw": self.NotSaveForWork,
      "num_images": self.ImageCount,
      "width": self.ImageWidth,
      "height": self.ImageHeight,
      "num_inference_steps": self.InferenceSteps,
      "guidance_scale": self.GuidanceScale,
      "sd_version": self.Model.StableDiffusionVersion,
      "presetStyle": self.Model.PresetStyle,
      "scheduler": self.Scheduler if self.Scheduler is not None else "LEONARDO",
      "public": self.Public,
      "tiling": self.Tiling if self.Tiling is not None else False,
      "leonardoMagic": self.LeonardoMagic if self.LeonardoMagic is not None else False,
      "poseToImage": self.ControlNet is not None,
      "elements": self.Elements if self.Elements is not None else [],
      **({"modelId": self.Model.Id} if self.Model.Id is not None else {}),
      **({"seed": self.Seed} if self.Seed is not None else {}),
    }

    if self.PromptMagic is not None:
      content.update({
        "leonardoMagic": True,
        "leonardoMagicVersion": self.PromptMagic.Version,
        "promptMagicStrength": self.PromptMagic.Strength,
        "highContrast": self.PromptMagic.HighContrast,
      })

    if self.Canvas is not None:
      content.update({
        "canvasRequest": True,
        "canvasRequestType": self.Canvas.RequestType,
        "canvasInitId": self.Canvas.InitId,
        "init_strength": self.Canvas.Strength,
        **({"canvasMaskId": self.Canvas.MaskId} if self.Canvas.MaskId is not None else {})
      })

    if self.ControlNet is not None:
      content.update({
        "poseToImage": True,
        "poseToImageType": self.ControlNet.Type,
        "weighting": self.ControlNet.Weight,
      })

    if self.PhotoReal is not None:
      content.update({
        "photoReal": True,
        "photoRealStrength": self.PhotoReal.Strength,
        "presetStyle": self.PhotoReal.Style,
      })

    if self.Alchemy is not None:
      content.update({
        "alchemy": True,
        "highResolution": self.Alchemy.HighResolution,
        "contrastRatio": self.Alchemy.ContrastBoost,
        "guidance_scale": self.Alchemy.Resonance,
      })
    else:
      content.update({
        "alchemy": False,
      })

    return content

