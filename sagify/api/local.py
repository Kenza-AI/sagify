# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os

from future.moves import subprocess

from sagify.log import logger


def train(dir, docker_tag, image_name):
    """
    Trains ML model(s) locally

    :param dir: [str], source root directory
    :param docker_tag: [str], the Docker tag for the image
    :param image_name: [str], The name of the Docker image
    """
    sagify_module_path = os.path.join(dir, 'sagify_base')
    local_train_script_path = os.path.join(sagify_module_path, 'local_test', 'train_local.sh')
    test_path = os.path.join(sagify_module_path, 'local_test', 'test_dir')

    if not os.path.isdir(test_path):
        raise ValueError("This is not a sagify directory: {}".format(dir))

    output = subprocess.check_output(
        [
            "{}".format(local_train_script_path),
            "{}".format(os.path.abspath(test_path)),
            docker_tag,
            image_name
        ]
    )
    logger.debug(output)


def deploy(dir, docker_tag, image_name):
    """
    Deploys ML models(s) locally

    :param dir: [str], source root directory
    :param docker_tag: [str], the Docker tag for the image
    :param image_name: [str], The name of the Docker image
    """
    sagify_module_path = os.path.join(dir, 'sagify_base')
    local_deploy_script_path = os.path.join(sagify_module_path, 'local_test', 'deploy_local.sh')
    test_path = os.path.join(sagify_module_path, 'local_test', 'test_dir')

    if not os.path.isdir(test_path):
        raise ValueError("This is not a sagify directory: {}".format(dir))

    output = subprocess.check_output(
        [
            "{}".format(local_deploy_script_path),
            "{}".format(os.path.abspath(test_path)),
            docker_tag,
            image_name
        ]
    )
    logger.debug(output)
