import leonardoaisdk

if __name__ == '__main__':
  from abstract import *
else:
  from ..abstract import *


class RestClient(AbstractClient):

  def __init__(self, token: str):
    self.sdk = leonardoaisdk.LeonardoAiSDK(token)

  def getUserInfo(self) -> UserInfo | None:
    response = self.sdk.user.get_user_self()
    if response.get_user_self_200_application_json_object is None:
      return None

    response = response.get_user_self_200_application_json_object
    return UserInfo(
      Id=response.user_details[0].user.id,
      Name=response.user_details[0].user.username,
    )

  def getGenerationById(self, generationId) -> Generation | None:
    response = self.sdk.generation.get_generation_by_id(generationId)
    if response.get_generation_by_id_200_application_json_object is None:
      return None

    response = response.get_generation_by_id_200_application_json_object.generations_by_pk
    return Generation(
      Id=response.id,
      CreatedAt=datetime.fromisoformat(response.created_at),
      GeneratedImages=[Image(Id=i.id, Url=i.url) for i in response.generated_images],
      ImageHeight=response.image_height,
      ImageWidth=response.image_width,
      Seed=response.seed,
      Status=response.status,
      Prompt=response.prompt,
      NegativePrompt=response.negative_prompt,
      SDVersion=response.sd_version,
    )


if __name__ == '__main__':
  import os

  client = RestClient(os.environ.get("API_KEY"))

  user = client.getUserInfo()
  print(user)
