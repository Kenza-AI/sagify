# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys
import click

from sagify.log import logger
from sagify.commands import ASCII_LOGO
from sagify.config.config import ConfigManager

click.disable_unicode_literals_warning = True


@click.command()
@click.option(u"--image-name", required=False, help="Docker image name")
@click.option(u"--aws-region", required=False, help="AWS Region to use in operations")
@click.option(u"--aws-profile", required=False, help="AWS Profile to use in operations")
@click.option(u"--python-version", required=False, help="Python version used when building")
@click.option(u"--requirements-dir", required=False, help="Path to requirements.txt")
def configure(image_name, aws_region, aws_profile, python_version, requirements_dir):
    """
    Command to configure SageMaker template
    """
    logger.info(ASCII_LOGO)
    _configure('.', image_name, aws_region, aws_profile, python_version, requirements_dir)


def _configure(config_dir, image_name, aws_region, aws_profile, python_version, requirements_dir):
    try:
        config_manager = ConfigManager(os.path.join(config_dir, '.sagify.json'))
        config = config_manager.get_config()

        if image_name is not None:
            config.image_name = image_name

        if aws_region is not None:
            config.aws_region = aws_region

        if aws_profile is not None:
            config.aws_profile = aws_profile

        if python_version is not None:
            config.python_version = python_version

        if requirements_dir is not None:
            config.requirements_dir = requirements_dir

        config_manager.set_config(config)

        logger.info("\nConfiguration updated successfully!\n")
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)
