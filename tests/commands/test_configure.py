from collections import namedtuple
from sagify.config.config import ConfigManager, Config
import os
from backports import tempfile

from unittest import TestCase

from sagify.commands.configure import _configure

Case = namedtuple('Case', 'description, image_name, aws_region, aws_profile, python_version, sagify_module_dir, requirements_dir, expected_config')

t1 = Case('t1: Configure IMAGE NAME', 'new-image-name', None, None, None, None, None,
          Config(image_name='new-image-name', aws_profile='', aws_region='',
                 python_version='', sagify_module_dir='', requirements_dir=''))

t2 = Case('t2: Configure AWS PROFILE', None, None, 'some-profile', None, None, None,
          Config(image_name='new-image-name', aws_profile='some-profile', aws_region='',
                 python_version='', sagify_module_dir='', requirements_dir=''))

t3 = Case('t3: Configure AWS REGION', None, 'us-east-2', None, None, None, None,
          Config(image_name='new-image-name', aws_profile='some-profile',
                 aws_region='us-east-2', python_version='', sagify_module_dir='', requirements_dir=''))

t4 = Case('t4: Configure PYTHON VERSION', None, None, None, '3.6', None, None,
          Config(image_name='new-image-name', aws_profile='some-profile', aws_region='us-east-2',
                 python_version='3.6', sagify_module_dir='', requirements_dir=''))

t5 = Case('t5: Configure REQUIREMENTS DIR', None, None, None, None, None, 'requirements.txt',
          Config(image_name='new-image-name', aws_profile='some-profile', aws_region='us-east-2',
                 python_version='3.6', sagify_module_dir='', requirements_dir='requirements.txt'))

t6 = Case('t6: Configure NOTHING', None, None, None, None, None, None,
          Config(image_name='new-image-name', aws_profile='some-profile', aws_region='us-east-2',
                 python_version='3.6', sagify_module_dir='', requirements_dir='requirements.txt'))

t7 = Case('t7: Configure EVERYTHING', 'some-other-image-name', 'us-east-1', 'some-other-profile', '2.7', None, 'other-requirements.txt',
          Config(image_name='some-other-image-name', aws_profile='some-other-profile', aws_region='us-east-1',
                 python_version='2.7', sagify_module_dir='', requirements_dir='other-requirements.txt'))

test_cases = [t1, t2, t3, t4, t5, t6, t7]


class ConfigureCommandTests(TestCase):

    def tests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for case in test_cases:
                try:
                    updateConfig(tmpdir, case.image_name, case.aws_region, case.aws_profile, case.python_version, case.requirements_dir)
                    config = ConfigManager(os.path.join(tmpdir, '.sagify.json')).get_config()
                    assert config.to_dict() == case.expected_config.to_dict()

                except AssertionError as e:
                    e.args = ('Test Case: {}'.format(case.description), e.args)
                    raise


def updateConfig(config_dir, image_name, aws_region, aws_profile, python_version, requirements_dir):
    _configure(config_dir, image_name, aws_region, aws_profile, python_version, requirements_dir)
