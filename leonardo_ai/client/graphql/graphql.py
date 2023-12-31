import base64

import requests
import json
from concurrent import futures

from PyQt5.QtCore import QByteArray, QBuffer, QIODevice

if __name__ == '__main__':
  import sys
  sys.path.append("..")

  from abstract import *
  from utils import *
  from model import *
else:
  from ..abstract import *
  from ..utils import *
  from .model import *

GQL_USER = """{
  id
  username
}"""

def _buildUser(response: dict):
  return UserInfo(
    Id=response['id'],
    Name=response['username'],
  )

GQL_IMAGE = """{
  id
  url
  user """ + GQL_USER + """
  likeCount
  generated_image_variation_generics(order_by: [{createdAt: desc}]) {
    id
    url
    status
    transformType
    upscale_details {
      alchemyRefinerCreative
      alchemyRefinerStrength
      oneClicktype
    }
  }
}"""

def _buildImageVariation(response: dict):
  v = ImageVariation(
    Id=response['id'],
    Url=response['url'],
    Status=response['status'],
    TransformationType=response['transformType']
  )
  if v.TransformationType == TransformationType.UPSCALE:
    v.UpscaleType = response['upscale_details'][0]['oneClicktype']
    if v.UpscaleType == UpscaleType.ALCHEMY_REFINER:
      v.AlchemyRefinerSettings = AlchemyRefinerSettings(
        Creative=response['upscale_details'][0]['alchemyRefinerCreative'],
        Strength=response['upscale_details'][0]['alchemyRefinerStrength'],
      )

  return v

def _buildImage(response: dict):
  return Image(
    Id=response['id'],
    Url=response['url'],
    Creator=_buildUser(response['user']),
    LikeCount=response['likeCount'],
    Variations=[_buildImageVariation(i) for i in response['generated_image_variation_generics']]
  )

GQL_MODEL = """{
  id
  name
  description
  modelHeight
  modelWidth
  coreModel
  createdAt
  sdVersion
  type
  nsfw
  public
  trainingStrength
  user """ + GQL_USER + """
  generated_image """ + GQL_IMAGE + """
}"""

def _buildModel(response: dict):
  return Model(
    Id=response['id'],
    Name=response['name'],
    Description=response['description'],
    NotSafeForWork=response['nsfw'],
    Public=response['public'],
    Height=response['modelHeight'],
    Width=response['modelWidth'],
    StableDiffusionVersion=response['sdVersion'],
    TrainingStrength=response['trainingStrength'],
    User=_buildUser(response['user']),
    PreviewImage=None
  )

GQL_GENERATION = """{
  id
  createdAt
  imageHeight
  imageWidth
  seed
  status
  prompt
  negativePrompt
  sdVersion
  nsfw
  public
  generated_images(order_by: [{url: desc}]) """ + GQL_IMAGE + """
  custom_model """ + GQL_MODEL + """
}"""

def _buildGeneration(response: dict) -> Generation:
  return Generation(
    Id=response['id'],
    CreatedAt=datetime.fromisoformat(response['createdAt']),
    GeneratedImages=[_buildImage(i) for i in response['generated_images']],
    ImageHeight=response['imageHeight'],
    ImageWidth=response['imageWidth'],
    Seed=response['seed'],
    Status=response['status'],
    Prompt=response['prompt'],
    NegativePrompt=response['negativePrompt'],
    SDVersion=response['sdVersion'],
    CustomModel=_buildModel(response['custom_model']) if response['custom_model'] is not None else None,
    Public=response['public'],
    NotSafeForWork=response['nsfw'],
  )

class GraphqlClient(AbstractClient):

  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.loginResponse = None
    self._userId = None

  def login(self):
    response = requests.get('https://app.leonardo.ai/api/auth/csrf')
    cookies = response.cookies

    response = requests.post('https://app.leonardo.ai/api/auth/callback/credentials?', data={
      "username": self.username,
      "password": self.password,
      "csrfToken": response.json()["csrfToken"],
      "json": 'true',
    }, cookies=cookies)
    cookies = response.cookies

    response = requests.get('https://app.leonardo.ai/api/auth/session', cookies=cookies)

    responseAsJson = response.json()
    self.loginResponse = responseAsJson

  @property
  def accessToken(self):
    if self.loginResponse is None:
      self.login()

    return self.loginResponse['accessToken']

  @property
  def userSub(self):
    if self.loginResponse is None:
      self.login()

    return self.loginResponse['user']['sub']

  @property
  def userId(self):
    if self._userId is None:
      self._userId = self.getUserInfo().Id

    return self._userId

  def _doGraphqlCall(self, operation: str, query: str, variables: dict):
    print(operation, query, variables)
    response = requests.post(
      url='https://api.leonardo.ai/v1/graphql',
      headers={
        "Authorization": f"Bearer {self.accessToken}",
        "Content-Type": "application/json"
      },
      data=json.dumps({
        "operation": operation,
        "query": query,
        "variables": variables,
      })
    )

    responseAsJson = response.json()
    if 'data' in responseAsJson:
      return responseAsJson['data']
    else:
      raise Exception("unable to do graphql call: " + response.text)

  def getUserInfo(self) -> UserInfo | None:
    response = self._doGraphqlCall(
      "GetUserDetails",
      """query GetUserDetails($userSub: String) {
  users(where: {user_details: {cognitoId: {_eq: $userSub}}}) """ + GQL_USER + """
  user_details(where: {cognitoId: { _eq: $userSub }}) {
    subscriptionGptTokens
    subscriptionModelTokens
    subscriptionTokens
    paidTokens
  }
}""",
      {"userSub": self.userSub})

    # remember user id for later use
    if self._userId is None:
      self._userId = response['users'][0]['id']

    user = _buildUser(response['users'][0])
    user.Token = TokenBalance(
        response['user_details'][0]['subscriptionGptTokens'],
        response['user_details'][0]['subscriptionModelTokens'],
        response['user_details'][0]['subscriptionTokens'],
        response['user_details'][0]['paidTokens'],
      )

    return user

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

    if ids is not None and len(ids) > 0:
      variables = {
        "where": {
          "id": {
            "_in": ids
          }
        },
        "offset": 0,
        "limit": len(ids)
      }
    else:
      variables = {
        "where": {
          "public": {"_eq": True},
          "name": {"_like": query},
          **({"official": {"_eq": official}} if official is not None else {}),
          **({"nsfw": {"_eq": notSafeForWork}} if notSafeForWork is not None else {}),
          **({"status": {
            **({"_eq": "COMPLETE"} if complete else {"_ne": "COMPLETE"})
          }} if complete is not None else {}),
        },
        "offset": offset,
        "limit": limit,
      }

    if orderByCreatedAsc is not None:
      variables.update({
        "order_by": {
          "createdAt": "asc" if orderByCreatedAsc else "desc"
        }
      })
    elif orderByNameAsc is not None:
      variables.update({
        "order_by": {
          "name": "asc" if orderByNameAsc else "desc"
        }
      })

    if favorites:
      variables.get("where").update({
        "user_favourite_custom_models": {
          "userId": {
            "_eq": self.userId
          }
        }
      })
      variables.get("where").pop("public")

    if own:
      variables.get("where").update({
        "userId": {
          "_eq": self.userId
        }
      })
      variables.get("where").pop("public")

    if category is not None:
      variables.get("where").update({
        "type": {
          "_eq": category
        }
      })

    variables.update({
      "generationsWhere": {
        "generated_images": {}
      }
    })

    response = self._doGraphqlCall(
      "GetFeedModels",
      """query GetFeedModels($order_by: [custom_models_order_by!] = [{ createdAt: desc }], $where: custom_models_bool_exp, $generationsWhere: generations_bool_exp, $limit: Int, $offset: Int) {
  custom_models(order_by: $order_by, where: $where, limit: $limit, offset: $offset) {
    ...ModelParts
    generations(where: $generationsWhere, limit: 1, order_by: [{ createdAt: asc }]) {
      generated_images(limit: 1, order_by: [{ likeCount: desc }]) """ + GQL_IMAGE + """
    }
  }
}
  
fragment ModelParts on custom_models """ + GQL_MODEL,
      variables
    )

    def getPreviewImage(model):
      if model['generated_image'] is not None:
        return _buildImage(model['generated_image'])
      if model['generations'] is not None and len(model['generations']) > 0:
        firstGen = model['generations'][0]
        if firstGen['generated_images'] is not None and len(firstGen['generated_images']) > 0:
          return _buildImage(firstGen['generated_images'][0])

      return None

    result = []
    for customModel in response['custom_models']:
      model = _buildModel(customModel)
      model.PreviewImage = getPreviewImage(customModel)
      result.append(model)

    return result

  def getElements(self, query: str = "%%", baseModel: str | None = None, offset: int = 0, limit: int = 64) -> List[Element]:
    response = self._doGraphqlCall(
      "GetElementsForModal",
      """query GetElementsForModal($offset: Int, $limit: Int, $where: loras_bool_exp) {
    loras(offset: $offset
    limit: $limit
    where: $where
    order_by: [ {
        sortOrder: asc
    }]) {
        akUUID
        name
        description
        urlImage
        baseModel
        weightDefault
        weightMin
        weightMax
    }
}""",
      {
        "where": {
          "name": {"_like": query},
          **({"baseModel": {"_eq": baseModel}} if baseModel is not None else {}),
        },
        "offset": offset,
        "limit": limit,
      }
    )

    response = response['loras']
    return [
      Element(
        Id=element['akUUID'],
        Name=element['name'],
        Description=element['description'],
        PreviewImageUrl=element['urlImage'],
        BaseModel=element['baseModel'],
        WeightDefault=element['weightDefault'],
        WeightMin=element['weightMin'],
        WeightMax=element['weightMax'],
      )
      for element in response
    ]

  def getGenerationById(self, generationId: str):
    response = self._doGraphqlCall(
      "GetAIGenerationFeed",
      """query GetAIGenerationFeed($where: generations_bool_exp = {}) {
  generations(limit: 1, where: $where) """ + GQL_GENERATION + """
}""",
      {"where": {"id": {"_eq": generationId}}}
    )

    if len(response['generations']) > 0:
      response = response['generations'][0]
      return _buildGeneration(response)
    else:
      return None

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
                     minLikeCount: int | None = None,
                     maxLikeCount: int | None = None,
                     status: JobStatus | None = None,
                     orderByCreatedAsc: bool | None = None,
                     orderByLikesAsc: bool | None = None,
                     offset: int = 0,
                     limit: int = 50) -> List[Generation]:

    orderBy = []
    where = { "generation": {  } }

    if not community: where.update({"userId": { "_eq": self.userId }})
    if prompt is not None: where["generation"].update({ "prompt": { "_ilike": f"""%{prompt}%""" } })
    if negativePrompt is not None: where["generation"].update({ "negativePrompt": { "_ilike": f"""%{negativePrompt}%""" } })
    if modelIds is not None and len(modelIds) > 0: where["generation"].update({ "modelId": { "_in": modelIds } })
    if status is not None: where["generation"].update({"status": {"_eq": status}})
    if notSafeForWork is not None: where["generation"].update({ "nsfw": { "_eq": notSafeForWork } })

    if minImageHeight is not None or maxImageHeight is not None:
      where["generation"].update({ "imageHeight": {  } })
      if minImageHeight is not None: where["generation"]["imageHeight"].update({ "_gte": minImageHeight })
      if maxImageHeight is not None: where["generation"]["imageHeight"].update({ "_lte": maxImageHeight })

    if minImageWidth is not None or maxImageWidth is not None:
      where["generation"].update({ "imageWidth": {  } })
      if minImageWidth is not None: where["generation"]["imageWidth"].update({ "_gte": minImageWidth })
      if maxImageWidth is not None: where["generation"]["imageWidth"].update({ "_lte": maxImageWidth })

    if minCreatedAt is not None or maxCreatedAt is not None:
      where["generation"].update({ "createdAt": {  } })
      if minCreatedAt is not None: where["generation"]["createdAt"].update({ "_gte": minCreatedAt.isoformat() })
      if maxCreatedAt is not None: where["generation"]["createdAt"].update({ "_lte": maxCreatedAt.isoformat() })

    if minLikeCount is not None or maxLikeCount is not None:
      where.update({ "likeCount": {  } })
      if minLikeCount is not None: where["likeCount"].update({ "_gte": minLikeCount })
      if maxLikeCount is not None: where["likeCount"].update({ "_lte": maxLikeCount })

    if orderByLikesAsc is not None: orderBy.append({ "likeCount": ("asc" if orderByLikesAsc else "desc") })
    if orderByCreatedAsc is not None: orderBy.append({ "createdAt": ("asc" if orderByCreatedAsc else "desc") })

    response = self._doGraphqlCall(
      "GetFeedImages",
      """query GetFeedImages($where: generated_images_bool_exp, $offset: Int, $limit: Int, $order_by: [generated_images_order_by!] = [{createdAt: desc}]) {
    generated_images(where: $where, offset: $offset, limit: $limit, order_by: $order_by) {
      generation """ + GQL_GENERATION + """
    }
}""",
      {
        "where": where,
        "order_by": orderBy if len(orderBy) > 0 else None,
        "offset": offset,
        "limit": limit,
      }
    )

    result = []
    for generatedImage in response['generated_images']:
      result.append(_buildGeneration(generatedImage['generation']))

    return result

  def deleteGenerationById(self, generationId: str) -> None:
    self._doGraphqlCall(
      "DeleteGeneration",
      """mutation DeleteGeneration($id: uuid!) {
  delete_generations_by_pk(id: $id) {
    id
  }
}""",
      { "id": generationId }
    )

  def _removeBackground(self, id: str, isVariation: bool) -> str:
    response = self._doGraphqlCall(
      "CreateNoBGJob",
      """mutation CreateNoBGJob($arg1: SDNobgJobInput!) {
  sdNobgJob(arg1: $arg1) {
    id
  }
}""",
      {"id": id, "isVariation": isVariation },
    )

    return response['sdNobgJob']['id']

  def removeImageBackground(self, imageId: str) -> str:
    return self._removeBackground(imageId, False)

  def removeImageVariationBackground(self, imageVariationId: str) -> str:
    return self._removeBackground(imageVariationId, True)

  def _unzoom(self, id: str, isVariation: bool = False) -> str:
    response = self._doGraphqlCall(
      "CreateUnzoomJob",
      """mutation CreateUnzoomJob($arg1: SDUnzoomInput!) {
  sdUnzoomJob(arg1: $arg1) {
    id
  }
}""",
      {
        "arg1": {
          "id": id,
          "isVariation": isVariation,
        },
      },
    )

    return response['sdUnzoomJob']['id']

  def unzoomImage(self, imageId: str):
    return self._unzoom(imageId, False)

  def unzoomImageVariation(self, imageVariationId: str):
    return self._unzoom(imageVariationId, True)

  def _upscale(self, id: str, isVariation: bool, upscaleType: UpscaleType, alchemyRefinerSettings: AlchemyRefinerSettings | None = None) -> str:
    variables = {"id": id , "isVariation": isVariation}

    if upscaleType == UpscaleType.DEFAULT: variables.update({})
    elif upscaleType == UpscaleType.ALTERNATIVE: variables.update({ "alternativeUpscale": True })
    elif upscaleType == UpscaleType.SMOOTH: variables.update({ "smoothUpscale": True })
    elif upscaleType == UpscaleType.HD: variables.update({ "hdUpscale": True })
    elif upscaleType == UpscaleType.ALCHEMY_REFINER: variables.update({
      "alchemyRefiner": True,
      "alchemyRefinerCreative": alchemyRefinerSettings.Creative,
      "alchemyRefinerStrength": alchemyRefinerSettings.Strength,
    })
    else: return None

    response = self._doGraphqlCall(
      "CreateUpscaleJob",
      """mutation CreateUpscaleJob($arg1: SDUpscaleJobInput!) {
  sdUpscaleJob(arg1: $arg1) {
    id
  }
}""",
      { "arg1": variables },
    )

    return response['sdUpscaleJob']['id']

  def upscaleImage(self, imageId: str, upscaleType: UpscaleType, alchemyRefinerSettings: AlchemyRefinerSettings | None = None) -> str:
    return self._upscale(imageId, False, upscaleType, alchemyRefinerSettings)

  def upscaleImageVariation(self, imageVariationId: str, upscaleType: UpscaleType, alchemyRefinerSettings: AlchemyRefinerSettings | None = None) -> str:
    return self._upscale(imageVariationId, True, upscaleType, alchemyRefinerSettings)

  def _prepareUpload(self, includeMask: bool) -> (uploadImageInfo, uploadImageInfo | None):
    response = self._doGraphqlCall(
      "uploadCanvasInitImage",
      """mutation uploadCanvasInitImage($includeMask: Boolean!) {
  uploadCanvasInitImage(
    arg1: {initExtension: "png", initFileType: "image/png", maskExtension: "png", maskFileType: "image/png"}
  ) {
    initFields
    initImageId
    initKey
    initUrl
    masksFields @include(if: $includeMask)
    masksImageId @include(if: $includeMask)
    masksKey @include(if: $includeMask)
    masksUrl @include(if: $includeMask)
  }
}""",
      {"includeMask": includeMask},
    )
    response = response['uploadCanvasInitImage']
    return (
      uploadImageInfo(response['initImageId'], response['initKey'], response['initUrl'], json.loads(response['initFields'])),
      uploadImageInfo(response['masksImageId'], response['masksKey'], response['masksUrl'], json.loads(response['masksFields'])) if includeMask else None,
    )

  def _uploadImage(self, url: str, name: str, image: QImage, fields: dict) -> requests.Response:
    rawImage = QByteArray()
    buffer = QBuffer(rawImage)
    buffer.open(QIODevice.WriteOnly)
    image.save(buffer, "PNG", 100)
    buffer.close()

    return requests.post(url, files={
      **{key: (None, value) for key, value in fields.items()},
      'file': (name, rawImage.data()),
    })

  def _createGenerationJob(self, parameter: generationParameter) -> str:
    response = self._doGraphqlCall(
      "CreateSDGenerationJob",
      """mutation CreateSDGenerationJob($arg1: SDGenerationInput!) {
  sdGenerationJob(arg1: $arg1) {
    generationId
  }
}""",
      {"arg1": parameter.ToArgs()},
    )

    response = response['sdGenerationJob']
    return response['generationId']

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
    gp = generationParameter(
      Prompt=prompt, NegativePrompt=negativePrompt,
      Model=modelParameter(
        Id=modelId, StableDiffusionVersion=sdVersion, PresetStyle=presetStyle,
      ),
      ImageCount=numberOfImages,
      ImageWidth=multipleOf(width, 8), ImageHeight=multipleOf(height, 8),
      InferenceSteps=inferenceSteps, GuidanceScale=guidanceScale,
      Scheduler=scheduler, Seed=seed, NotSafeForWork=notSafeForWork, Public=public,
    )
    if photoRealStrength is not None:
      gp.PhotoReal = photoRealParameter(
        Strength=photoRealStrength,
        HighContrast=photoRealHighContrast,
        Style=photoRealStyle,
      )

    if alchemyContrastBoost is not None:
      gp.Alchemy = alchemyParameter(
        HighResolution=alchemyHighResolution,
        ContrastBoost=alchemyContrastBoost,
        Resonance=alchemyResonance,
      )

    if promptMagicStrength is not None:
      gp.PromptMagic = promptMagicParameter(
        Strength=promptMagicStrength,
        HighContrast=promptMagicHighContrast,
        Version=promptMagicVersion,
      )

    return self._createGenerationJob(gp)


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
                              imageStrength: float = 1.0,
                              seed: int | None = None,
                              ) -> str:
    if mask is None:
      mask = QImage(image.width(), image.height(), QImage.Format_Grayscale8)
      mask.fill(0)

    iImage, iMask = self._prepareUpload(True)

    # upload images in parallel
    with futures.ThreadPoolExecutor() as e:
      uploads = [
        e.submit(self._uploadImage, iImage.Url, 'init.png', image, iImage.Fields),
        e.submit(self._uploadImage, iMask.Url, 'mask.png', mask, iMask.Fields)
      ]

    # wait for all uploads to finish
    for upload in uploads:
      if upload.result().status_code != 204:
        raise Exception(f"unable to upload image: unexpected response code: {upload.result().status_code}")

    return self._createGenerationJob(generationParameter(
      Prompt=prompt, NegativePrompt=negativePrompt,
      Model=modelParameter(
        Id=modelId, StableDiffusionVersion=sdVersion, PresetStyle=presetStyle,
      ),
      ImageCount=numberOfImages,
      ImageWidth=multipleOf(image.width(), 8), ImageHeight=multipleOf(image.height(), 8),
      Canvas=canvasParameter(
        InitId=iImage.Id, MaskId=iMask.Id, Strength=imageStrength, RequestType="INPAINT",
      ),
      InferenceSteps=inferenceSteps, GuidanceScale=guidanceScale,
      Scheduler=scheduler, Seed=seed, NotSafeForWork=notSafeForWork, Public=public,
    ))

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
    iImage, _ = self._prepareUpload(False)
    uResponse = self._uploadImage(iImage.Url, 'init.png', image, iImage.Fields)

    if uResponse.status_code != 204:
      raise Exception(f"unable to upload image: unexpected response code: {uResponse.status_code}")

    gp = generationParameter(
      Prompt=prompt, NegativePrompt=negativePrompt,
      Model=modelParameter(
        Id=modelId, StableDiffusionVersion=sdVersion, PresetStyle=presetStyle,
      ),
      ImageCount=numberOfImages,
      ImageWidth=multipleOf(image.width(), 8), ImageHeight=multipleOf(image.height(), 8),
      Canvas=canvasParameter(
        InitId=iImage.Id, Strength=imageStrength, RequestType="IMG2IMG",
      ),
      Tiling=tiling,
      InferenceSteps=inferenceSteps, GuidanceScale=guidanceScale,
      Scheduler=scheduler, Seed=seed, NotSafeForWork=notSafeForWork, Public=public,
    )
    if poseToImage is not None:
      gp.ControlNet = controlNetParameter(Type=poseToImage, Weight=controlnetWeight)

    if alchemyContrastBoost is not None:
      gp.Alchemy = alchemyParameter(
        HighResolution=alchemyHighResolution,
        ContrastBoost=alchemyContrastBoost,
        Resonance=alchemyResonance,
      )

    return self._createGenerationJob(gp)

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
    if mask is None:
      mask = QImage(image.width(), image.height(), QImage.Format_Grayscale8)
      mask.fill(0)

    iImage, iMask = self._prepareUpload(True)

    # upload images in parallel
    with futures.ThreadPoolExecutor() as e:
      uploads = [
        e.submit(self._uploadImage, iImage.Url, 'init.png', image, iImage.Fields),
        e.submit(self._uploadImage, iMask.Url, 'mask.png', mask, iMask.Fields)
      ]

    # wait for all uploads to finish
    for upload in uploads:
      if upload.result().status_code != 204:
        raise Exception(f"unable to upload image: unexpected response code: {upload.result().status_code}")

    gp = generationParameter(
      Prompt=prompt, NegativePrompt=negativePrompt,
      Model=modelParameter(
        Id=modelId, StableDiffusionVersion=sdVersion, PresetStyle=presetStyle,
      ),
      ImageCount=numberOfImages,
      ImageWidth=multipleOf(image.width(), 8), ImageHeight=multipleOf(image.height(), 8),
      Canvas=canvasParameter(
        InitId=iImage.Id, MaskId=iMask.Id, Strength=imageStrength, RequestType="SKETCH2IMG",
      ),
      InferenceSteps=inferenceSteps, GuidanceScale=guidanceScale,
      Scheduler=scheduler, Seed=seed, NotSafeForWork=notSafeForWork, Public=public,
    )

    return self._createGenerationJob(gp)

  def createLcmSketch2Image(self,
                            prompt: str,
                            image: QImage,
                            negativePrompt: str = "",
                            strength: float = 0.8,
                            guidance: int = 7,
                            style: str | None = None,
                            instantRefine: bool | None = None,
                            seed: int | None = None,
                            ) -> QImage:

    buffer = QByteArray()
    qbuffer = QBuffer(buffer)
    qbuffer.open(QIODevice.WriteOnly)
    image.save(qbuffer, "JPEG")

    dataurl = "data:image/jpeg;base64," + buffer.toBase64().data().decode()

    response = self._doGraphqlCall(
      "CreateLCMGenerationJob",
      """mutation CreateLCMGenerationJob($arg1: LcmGenerationInput!) {
  lcmGenerationJob(arg1: $arg1) {
    imageDataUrl
  }
}""",
      {
        "arg1": {
          "prompt": prompt,
          "negativePrompt": negativePrompt,
          "strength": strength,
          "guidance": guidance,
          "style": style,
          "seed": seed,
          "instantRefine": instantRefine,
          "imageDataUrl": dataurl,
        }
      }
    )

    _, dataB64 = response['lcmGenerationJob']['imageDataUrl'][0].split(',', 1)
    return QImage.fromData(base64.b64decode(dataB64))

if __name__ == '__main__':
  import os

  client = GraphqlClient(os.environ.get("USERNAME"), os.environ.get("PASSWORD"))

  print(client.getUserInfo())
