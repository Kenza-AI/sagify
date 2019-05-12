# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from sagify.config.config import ConfigManager
from distutils.dir_util import copy_tree

_FILE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def _template_creation(app_name, aws_profile, aws_region, python_version, output_dir):
    sagify_module_name = 'sagify'

    sagify_exists = os.path.exists(os.path.join(output_dir, sagify_module_name))
    if sagify_exists:
        raise ValueError(
            "There is a sagify directory/module already. "
            "Please, rename it in order to use sagify."
        )

    Path(output_dir).mkdir(exist_ok=True)
    Path(os.path.join(output_dir, '__init__.py')).touch()

    # Set 'sagify module' directory up
    copy_tree(os.path.join(_FILE_DIR_PATH, '../template'), output_dir)

    # Set configuration file up
    config_manager = ConfigManager(os.path.join('.sagify.json'))
    config = config_manager.get_config()

    config.image_name = app_name
    config.aws_region = aws_region
    config.aws_profile = aws_profile
    config.sagify_module_dir = app_name
    config.python_version = python_version
    config_manager.set_config(config)


def init(sagify_app_name, aws_profile, aws_region, python_version):
    """
    Initializes a SageMaker template

    :param dir: [str], source root directory
    :param sagify_app_name: [str], name for sagify app
    :param aws_profile: [str], preferred aws profile name on current host
    :param aws_region: [str], preferred aws region. Example: 'us-east-1'
    :param python_version: [str], preferred Python version. Options: 3.6 or 2.7.
    """
    if python_version not in {'2.7', '3.6'}:
        raise ValueError("Invalid Python version. Valid options: 2.7 or 3.6")

    _template_creation(
        app_name=sagify_app_name,
        aws_profile=aws_profile,
        aws_region=aws_region,
        python_version=python_version,
        output_dir=sagify_app_name
    )
