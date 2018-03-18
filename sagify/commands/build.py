# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys

from future.moves import subprocess

import click

from sagify.commands import ASCII_LOGO
from sagify.log import logger


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.')
def build(dir):
    """
    Command to build SageMaker app
    """
    logger.info(ASCII_LOGO)
    logger.info("Started building SageMaker Docker image. It will take some minutes...\n")

    sagify_module_path = os.path.join(dir, 'sagify')

    build_script_path = os.path.join(sagify_module_path, 'build.sh')
    dockerfile_path = os.path.join(sagify_module_path, 'Dockerfile')

    train_file_path = os.path.join(sagify_module_path, 'training', 'train')
    serve_file_path = os.path.join(sagify_module_path, 'prediction', 'serve')

    if not os.path.isfile(build_script_path) or not os.path.isfile(train_file_path) or not \
            os.path.isfile(serve_file_path):
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)

    os.chmod(train_file_path, 0o777)
    os.chmod(serve_file_path, 0o777)

    try:
        subprocess.check_output(
            [
                "{}".format(build_script_path),
                "{}".format(sagify_module_path),
                "{}".format(dockerfile_path)
            ]
        )

        logger.info("Docker image built successfully!")
    except Exception as e:
        logger.info("{}".format(e))
        return
