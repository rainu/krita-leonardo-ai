from dataclasses import dataclass

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
class promptMagicParameter:
  Strength: float
  HighContrast: bool
  Version: str

@dataclass
class photoRealParameter:
  Strength: float
  ContrastRatio: float
  Style: str

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
class generationParameter:
  Prompt: str
  NegativePrompt: str
  ImageCount: int
  ImageWidth: int
  ImageHeight: int
  InferenceSteps: int
  GuidanceScale: int
  StableDiffusionVersion: str
  ModelId: str | None
  Public: bool
  NotSaveForWork: bool
  LeonardoMagic: bool | None = None
  Alchemy: bool | None = None
  Tiling: bool | None = None
  Canvas: canvasParameter | None = None
  PromptMagic: promptMagicParameter | None = None
  PhotoReal: photoRealParameter | None = None
  ControlNet: controlNetParameter | None = None
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
      "sd_version": self.StableDiffusionVersion,
      "scheduler": self.Scheduler if self.Scheduler is not None else "LEONARDO",
      "public": self.Public,
      "tiling": self.Tiling if self.Tiling is not None else False,
      "leonardoMagic": self.LeonardoMagic if self.LeonardoMagic is not None else False,
      "poseToImage": self.ControlNet is not None,
      "elements": [],
      **({"alchemy": self.Alchemy } if self.Alchemy is not None else {}),
      **({"modelId": self.ModelId } if self.ModelId is not None else {}),
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
        "contrastRatio": self.PhotoReal.ContrastRatio,
      })

    return content

