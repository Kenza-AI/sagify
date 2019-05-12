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
@click.option(u"-d", u"--dir", required=True, help="Sagify directory")
@click.option(u"--image-name", required=False, help="Docker image name")
@click.option(u"--aws-region", required=False, help="AWS Region to use in operations")
@click.option(u"--aws-profile", required=False, help="AWS Profile to use in operations")
@click.option(u"--python-version", required=False, help="Python version used when building")
def configure(dir, image_name, aws_region, aws_profile, python_version):
    """
    Command to configure SageMaker template
    """
    logger.info(ASCII_LOGO)
    _configure(dir, image_name, aws_region, aws_profile, python_version)


def _configure(dir, image_name, aws_region, aws_profile, python_version):
    try:
        config_manager = ConfigManager(os.path.join(dir, 'sagify', 'config.json'))
        config = config_manager.get_config()

        if image_name is not None:
            config.image_name = image_name

        if aws_region is not None:
            config.aws_region = aws_region

        if aws_profile is not None:
            config.aws_profile = aws_profile

        if python_version is not None:
            config.python_version = python_version

        config_manager.set_config(config)

        logger.info("\nConfiguration updated successfully!\n")
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)
