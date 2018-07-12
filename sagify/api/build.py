# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os

from future.moves import subprocess

from sagify.log import logger


def build(dir, requirements_dir, docker_tag):
    """
    Builds a Docker image that contains code under the given source root directory.

    Assumes that Docker is installed and running locally.

    :param dir: [str], source root directory
    :param requirements_dir: [str], path to requirements.txt
    """
    sagify_module_path = os.path.relpath(os.path.join(dir, 'sagify/'))

    build_script_path = os.path.join(sagify_module_path, 'build.sh')
    dockerfile_path = os.path.join(sagify_module_path, 'Dockerfile')

    train_file_path = os.path.join(sagify_module_path, 'training', 'train')
    serve_file_path = os.path.join(sagify_module_path, 'prediction', 'serve')
    executor_file_path = os.path.join(sagify_module_path, 'executor.sh')

    if not os.path.isfile(build_script_path) or not os.path.isfile(train_file_path) or not \
            os.path.isfile(serve_file_path):
        raise ValueError("This is not a sagify directory: {}".format(dir))

    os.chmod(train_file_path, 0o777)
    os.chmod(serve_file_path, 0o777)
    os.chmod(executor_file_path, 0o777)

    target_dir_name = os.path.basename(os.path.normpath(dir))

    output = subprocess.check_output(
        [
            "{}".format(build_script_path),
            "{}".format(os.path.relpath(dir)),
            "{}".format(os.path.relpath(target_dir_name)),
            "{}".format(dockerfile_path),
            "{}".format(os.path.relpath(requirements_dir)),
            docker_tag
        ]
    )
    logger.debug(output)
