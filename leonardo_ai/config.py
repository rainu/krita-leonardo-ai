import json
import logging
import os.path

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
        json.dump(self.__data, file)
    except Exception as e:
      logging.warning("Unable to save config file.", e)


  def set(self, key: str, value: any):
    self.__data[key] = value
    self.save()

  def get(self, key: str, default: any = None) -> any:
    if key in self.__data: return self.__data[key]
    return default
