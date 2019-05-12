import os
import json
from collections import OrderedDict


class Config(object):
    def __init__(self, image_name, aws_profile, aws_region, python_version):
        self.image_name = image_name
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        self.python_version = python_version

    def to_dict(self):
        return OrderedDict(self.__dict__.items())

    @classmethod
    def from_dict(cls, input_dict):
        return Config(
            image_name=input_dict['image_name'],
            aws_profile=input_dict['aws_profile'],
            aws_region=input_dict['aws_region'],
            python_version=input_dict['python_version']
        )


class ConfigManager(object):
    def __init__(self, config_file_path):
        self._config_file_path = config_file_path

        if not os.path.isfile(config_file_path):
            self.set_config(Config(
                image_name='',
                aws_profile='',
                aws_region='',
                python_version=''
            ))

    def get_config(self):
        with open(self._config_file_path) as config_file:
            config_content = config_file.read()

        return Config.from_dict(json.loads(config_content))

    def set_config(self, config):
        with open(self._config_file_path, 'w') as config_file:
            json.dump(config.to_dict(), config_file, indent=4)
