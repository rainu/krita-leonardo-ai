import requests
import json
from concurrent import futures

from PyQt5.QtCore import QByteArray, QBuffer, QIODevice

if __name__ == '__main__':
  import sys
  sys.path.append("..")

  from client.abstract import *
  from client.utils import *
  from model import *
else:
  from ..abstract import *
  from ..utils import *
  from .model import *

class GraphqlClient(AbstractClient):

  def __init__(self, username, password):
    response = requests.get('https://app.leonardo.ai/api/auth/csrf')
    cookies = response.cookies

    response = requests.post('https://app.leonardo.ai/api/auth/callback/credentials?', data={
      "username": username,
      "password": password,
      "csrfToken": response.json()["csrfToken"],
      "json": 'true',
    }, cookies=cookies)
    cookies = response.cookies

    response = requests.get('https://app.leonardo.ai/api/auth/session', cookies=cookies)

    responseAsJson = response.json()
    self.accessToken = responseAsJson['accessToken']
    self.userSub = responseAsJson['user']['sub']

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
          users(where: {user_details: {cognitoId: {_eq: $userSub}}}) {
              id
              username
          }
      }""",
      {"userSub": self.userSub})

    return UserInfo(
      response['users'][0]['id'],
      response['users'][0]['username'],
    )

  def getModels(self,
                query: str = "%%",
                official: bool | None = None,
                complete: bool | None = None,
                notSaveForWork: bool | None = None,
                offset: int = 0,
                limit: int = 50) -> List[Model]:
    response = self._doGraphqlCall(
      "",
      """query GetFeedModels($order_by: [custom_models_order_by!] = [ { createdAt: desc }], $where: custom_models_bool_exp, $limit: Int, $offset: Int) {
    custom_models(order_by: $order_by
    where: $where
    limit: $limit
    offset: $offset) {
        ...ModelParts
    }
}

fragment ModelParts on custom_models {
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
    user {
        id
        username
    }
    generated_image {
        id
        url
    }
}""",
      {
        "where": {
          "public": { "_eq": True },
          "name": { "_like": query },
          **({ "official": { "_eq": official } } if official is not None else {}),
          **({ "nsfw": { "_eq": notSaveForWork } } if notSaveForWork is not None else {}),
          **({ "status": {
            **({"_eq": "COMPLETE"} if complete else { "_ne": "COMPLETE" } )
          }} if complete is not None else {}),
        },
        "offset": offset,
        "limit": limit,
      }
    )

    response = response['custom_models']
    return [
      Model(
        Id=model['id'],
        Name=model['name'],
        Description=model['description'],
        NotSaveForWork=model['nsfw'],
        Public=model['public'],
        Height=model['modelHeight'],
        Width=model['modelWidth'],
        TrainingStrength=model['trainingStrength'],
        User=UserInfo(
          Id=model['user']['id'],
          Name=model['user']['username'],
        ),
        PreviewImage=Image(
          Id=model['generated_image']['id'],
          Url=model['generated_image']['url'],
        ) if model['generated_image'] is not None else None
      )
      for model in response
    ]

  def getGenerationById(self, generationId: str):
    response = self._doGraphqlCall(
      "GetAIGenerationFeed",
      """query GetAIGenerationFeed($where: generations_bool_exp = {}) {
  generations(
    limit: 1
    where: $where
  ) {
    id
    createdAt
    imageHeight
    imageWidth
    seed
    status
    prompt
    negativePrompt
    sdVersion
    generated_images(order_by: [{url: desc}]) {
      id
      url
    }
  }
}
""",
      {"where": {"id": {"_eq": generationId}}}
    )

    response = response['generations'][0]
    return Generation(
      Id=response['id'],
      CreatedAt=datetime.fromisoformat(response['createdAt']),
      GeneratedImages=[Image(Id=i['id'], Url=i['url']) for i in response['generated_images']],
      ImageHeight=response['imageHeight'],
      ImageWidth=response['imageWidth'],
      Seed=response['seed'],
      Status=response['status'],
      Prompt=response['prompt'],
      NegativePrompt=response['negativePrompt'],
      SDVersion=response['sdVersion'],
    )

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
                            notSaveForWork: bool = True,
                            numberOfImages: int = 4,
                            inferenceSteps: int = 10,
                            guidanceScale: int = 7,
                            photoRealStrength: float | None = None,
                            photoRealContrastRatio: float | None = None,
                            photoRealStyle: str = "CINEMATIC",
                            promptMagicStrength: float | None = None,
                            promptMagicHighContrast: bool | None = None,
                            promptMagicVersion: str = "v2",
                            useAlchemy: bool = False,
                            tiling: bool = False,
                            sdVersion: str = "v1_5",
                            modelId: str | None = None,
                            scheduler: str = "LEONARDO",
                            public: bool = False,
                            seed: int | None = None,
                            ) -> str:
    gp = generationParameter(
      Prompt=prompt, NegativePrompt=negativePrompt, ModelId=modelId, StableDiffusionVersion=sdVersion,
      ImageCount=numberOfImages,
      ImageWidth=multipleOf(width, 8), ImageHeight=multipleOf(height, 8),
      InferenceSteps=inferenceSteps, GuidanceScale=guidanceScale, Alchemy=useAlchemy,
      Scheduler=scheduler, Seed=seed, NotSaveForWork=notSaveForWork, Public=public,
    )
    if photoRealStrength is not None:
      gp.PhotoReal = photoRealParameter(
        Strength=photoRealStrength,
        ContrastRatio=photoRealContrastRatio,
        Style=photoRealStyle,
      )
      gp.Alchemy = True #photoreal needs alchemy

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
                              notSaveForWork: bool = True,
                              numberOfImages: int = 4,
                              inferenceSteps: int = 10,
                              guidanceScale: int = 7,
                              sdVersion: str = "v1_5",
                              modelId: str | None = None,
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
      Prompt=prompt, NegativePrompt=negativePrompt, ModelId=modelId, StableDiffusionVersion=sdVersion,
      ImageCount=numberOfImages,
      ImageWidth=multipleOf(image.width(), 8), ImageHeight=multipleOf(image.height(), 8),
      Canvas=canvasParameter(
        InitId=iImage.Id, MaskId=iMask.Id, Strength=imageStrength, RequestType="INPAINT",
      ),
      InferenceSteps=inferenceSteps, GuidanceScale=guidanceScale,
      Scheduler=scheduler, Seed=seed, NotSaveForWork=notSaveForWork, Public=public,
    ))

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
    iImage, _ = self._prepareUpload(False)
    uResponse = self._uploadImage(iImage.Url, 'init.png', image, iImage.Fields)

    if uResponse.status_code != 204:
      raise Exception(f"unable to upload image: unexpected response code: {uResponse.status_code}")

    gp = generationParameter(
      Prompt=prompt, NegativePrompt=negativePrompt, ModelId=modelId, StableDiffusionVersion=sdVersion,
      ImageCount=numberOfImages,
      ImageWidth=multipleOf(image.width(), 8), ImageHeight=multipleOf(image.height(), 8),
      Canvas=canvasParameter(
        InitId=iImage.Id, Strength=imageStrength, RequestType="IMG2IMG",
      ),
      Tiling=tiling, Alchemy=useAlchemy,
      InferenceSteps=inferenceSteps, GuidanceScale=guidanceScale,
      Scheduler=scheduler, Seed=seed, NotSaveForWork=notSaveForWork, Public=public,
    )
    if poseToImage is not None:
      gp.ControlNet = controlNetParameter(Type=poseToImage, Weight=controlnetWeight)

    return self._createGenerationJob(gp)

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
      Prompt=prompt, NegativePrompt=negativePrompt, ModelId=modelId, StableDiffusionVersion=sdVersion,
      ImageCount=numberOfImages,
      ImageWidth=multipleOf(image.width(), 8), ImageHeight=multipleOf(image.height(), 8),
      Canvas=canvasParameter(
        InitId=iImage.Id, MaskId=iMask.Id, Strength=imageStrength, RequestType="SKETCH2IMG",
      ),
      InferenceSteps=inferenceSteps, GuidanceScale=guidanceScale,
      Scheduler=scheduler, Seed=seed, NotSaveForWork=notSaveForWork, Public=public,
    )

    return self._createGenerationJob(gp)

if __name__ == '__main__':
  import os

  client = GraphqlClient(os.environ.get("USERNAME"), os.environ.get("PASSWORD"))

  print(client.getModels())
