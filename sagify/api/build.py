# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os

from future.moves import subprocess

from sagify.log import logger


def build(source_dir, requirements_dir, image_name, docker_tag, python_version):
    """
    Builds a Docker image that contains code under the given source root directory.

    Assumes that Docker is installed and running locally.

    :param source_dir: [str], source root directory
    :param requirements_dir: [str], path to requirements.txt
    :param image_name: [str], The name of the Docker image
    :param docker_tag: [str], the Docker tag for the image
    """
    sagify_module_path = os.path.relpath(os.path.join(source_dir, 'sagify_base/'))

    build_script_path = os.path.join(sagify_module_path, 'build.sh')
    dockerfile_path = os.path.join(sagify_module_path, 'Dockerfile')

    train_file_path = os.path.join(sagify_module_path, 'training', 'train')
    serve_file_path = os.path.join(sagify_module_path, 'prediction', 'serve')
    executor_file_path = os.path.join(sagify_module_path, 'executor.sh')

    if not os.path.isfile(build_script_path) or not os.path.isfile(train_file_path) or not \
            os.path.isfile(serve_file_path):
        raise ValueError("This is not a sagify directory: {}".format(source_dir))

    os.chmod(train_file_path, 0o777)
    os.chmod(serve_file_path, 0o777)
    os.chmod(executor_file_path, 0o777)

    target_dir_name = os.path.basename(os.path.normpath(source_dir))

    output = subprocess.check_output(
        [
            "{}".format(build_script_path),
            "{}".format(os.path.relpath(source_dir)),
            "{}".format(os.path.relpath(target_dir_name)),
            "{}".format(dockerfile_path),
            "{}".format(os.path.relpath(requirements_dir)),
            docker_tag,
            image_name,
            python_version
        ]
    )
    logger.debug(output)
