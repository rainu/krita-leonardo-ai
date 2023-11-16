import json
import logging
import os.path
from enum import Enum

class ConfigRegistry(Enum):
  LEONARDO_CLIENT_TYPE = "leonardo.client.type"
  LEONARDO_CLIENT_GQL_USERNAME = "leonardo.client.gql.username"
  LEONARDO_CLIENT_GQL_PASSWORD = "leonardo.client.gql.password"
  LEONARDO_CLIENT_REST_KEY = "leonardo.client.rest.key"

  GENERAL_NSFW = "general.nsfw"
  GENERAL_PUBLIC = "general.public"

  IMAGE_CACHE_DIRECTORY = "image.cache.directory"

class Config:
  __instance = None
  __configLocation = None
  __data = {}

  def __init__(self):
    raise RuntimeError('Call instance() instead')

  @classmethod
  def instance(cls):
    if cls.__instance is None:
      cls.__instance = cls.__new__(cls)
      cls.__instance.__configLocation = os.path.join(os.path.dirname(__file__), "config.json")
      cls.__instance.__data = {}
      cls.__instance.load()

    return cls.__instance

  def load(self):
    if os.path.isfile(self.__configLocation):
      try:
        with open(self.__configLocation, 'r') as file:
          self.__data = json.load(file)
      except Exception as e:
        logging.warning("Unable to load config file.", e)
    else:
      self.save() # create an empty file

  def save(self):
    try:
      with open(self.__configLocation, 'w') as file:
        json.dump(self.__data, file, indent=2)
    except Exception as e:
      logging.warning("Unable to save config file.", e)


  def set(self, key: str | ConfigRegistry, value: any):
    if isinstance(key, ConfigRegistry):
      key = key.value

    self.__data[key] = value
    self.save()

  def get(self, key: str | ConfigRegistry, default: any = None) -> any:
    if isinstance(key, ConfigRegistry):
      key = key.value

    if key in self.__data: return self.__data[key]
    return default
