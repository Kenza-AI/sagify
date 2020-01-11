# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys

import click

from sagify.api import build as api_build
from sagify.commands import ASCII_LOGO
from sagify.log import logger
from future.moves import subprocess
from sagify.config.config import ConfigManager
import os

click.disable_unicode_literals_warning = True


@click.command()
@click.pass_obj
def build(obj):
    """
    Command to build SageMaker app
    """
    logger.info(ASCII_LOGO)
    logger.info("Started building SageMaker Docker image. It will take some minutes...\n")

    try:
        config_file_path = os.path.join('.sagify.json')
        if not os.path.isfile(config_file_path):
            raise ValueError()

        config = ConfigManager(config_file_path).get_config()
        api_build.build(
            source_dir=config.sagify_module_dir,
            requirements_dir=config.requirements_dir,
            docker_tag=obj['docker_tag'],
            image_name=config.image_name,
            python_version=config.python_version)

        logger.info("Docker image built successfully!")
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except subprocess.CalledProcessError as e:
        logger.debug(e.output)
        raise
    except Exception as e:
        logger.info("{}".format(e))
        sys.exit(-1)
