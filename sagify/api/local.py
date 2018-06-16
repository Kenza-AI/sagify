# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os

from future.moves import subprocess


def train(dir):
    """
    Trains ML model(s) locally

    :param dir: [str], source root directory
    """
    sagify_module_path = os.path.join(dir, 'sagify')
    local_train_script_path = os.path.join(sagify_module_path, 'local_test', 'train_local.sh')
    test_path = os.path.join(sagify_module_path, 'local_test', 'test_dir')

    if not os.path.isdir(test_path):
        raise ValueError("This is not a sagify directory: {}".format(dir))

    subprocess.check_output(
        [
            "{}".format(local_train_script_path),
            "{}".format(os.path.abspath(test_path))
        ]
    )


def deploy(dir):
    """
    Deploys ML models(s) locally

    :param dir: [str], source root directory
    """
    sagify_module_path = os.path.join(dir, 'sagify')
    local_deploy_script_path = os.path.join(sagify_module_path, 'local_test', 'deploy_local.sh')
    test_path = os.path.join(sagify_module_path, 'local_test', 'test_dir')

    if not os.path.isdir(test_path):
        raise ValueError("This is not a sagify directory: {}".format(dir))

    subprocess.check_output(
        [
            "{}".format(local_deploy_script_path),
            "{}".format(os.path.abspath(test_path))
        ]
    )
