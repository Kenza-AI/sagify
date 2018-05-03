import json
from collections import OrderedDict


class Config(object):
    def __init__(self, image_name, aws_profile, aws_region):
        self.image_name = image_name
        self.aws_profile = aws_profile
        self.aws_region = aws_region

    def to_dict(self):
        return OrderedDict(self.__dict__.items())

    @classmethod
    def from_dict(cls, input_dict):
        return Config(
            image_name=input_dict['image_name'],
            aws_profile=input_dict['aws_profile'],
            aws_region=input_dict['aws_region']
        )


class ConfigManager(object):
    def __init__(self, config_file_path):
        self._config_file_path = config_file_path

    def get_config(self):
        with open(self._config_file_path) as config_file:
            config_content = config_file.read()

        return Config.from_dict(json.loads(config_content))
