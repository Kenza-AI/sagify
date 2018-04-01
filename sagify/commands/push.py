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
def push(dir):
    """
    Command to push Docker image to AWS ECS
    """
    logger.info(ASCII_LOGO)
    logger.info(
        "Started pushing Docker image to AWS ECS. It will take some time. Please, be patient...\n"
    )

    sagify_module_path = os.path.relpath(os.path.join(dir, 'sagify/'))

    push_script_path = os.path.join(sagify_module_path, 'push.sh')

    if not os.path.isfile(push_script_path):
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)

    try:
        subprocess.check_output(["{}".format(push_script_path)])

        logger.info("Docker image pushed to ECS successfully!")
    except Exception as e:
        logger.info("{}".format(e))
        return
