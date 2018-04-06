# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys

from future.moves import subprocess

import click

from sagify.commands import ASCII_LOGO
from sagify.log import logger

click.disable_unicode_literals_warning = True


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.', help="Path to sagify module")
@click.option(u"-r", u"--requirements-dir", required=True, help="Path to requirements.txt file")
def build(dir, requirements_dir):
    """
    Command to build SageMaker app
    """
    logger.info(ASCII_LOGO)
    logger.info("Started building SageMaker Docker image. It will take some minutes...\n")

    sagify_module_path = os.path.relpath(os.path.join(dir, 'sagify/'))

    build_script_path = os.path.join(sagify_module_path, 'build.sh')
    dockerfile_path = os.path.join(sagify_module_path, 'Dockerfile')

    train_file_path = os.path.join(sagify_module_path, 'training', 'train')
    serve_file_path = os.path.join(sagify_module_path, 'prediction', 'serve')
    executor_file_path = os.path.join(sagify_module_path, 'executor.sh')

    if not os.path.isfile(build_script_path) or not os.path.isfile(train_file_path) or not \
            os.path.isfile(serve_file_path):
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)

    os.chmod(train_file_path, 0o777)
    os.chmod(serve_file_path, 0o777)
    os.chmod(executor_file_path, 0o777)

    target_dir_name = os.path.basename(os.path.normpath(dir))

    try:
        subprocess.check_output(
            [
                "{}".format(build_script_path),
                "{}".format(os.path.relpath(dir)),
                "{}".format(os.path.relpath(target_dir_name)),
                "{}".format(dockerfile_path),
                "{}".format(os.path.relpath(requirements_dir))
            ]
        )

        logger.info("Docker image built successfully!")
    except Exception as e:
        logger.info("{}".format(e))
        return
