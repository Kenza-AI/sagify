# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys

from future.moves import subprocess

import click

from sagify.commands import ASCII_LOGO
from sagify.log import logger

click.disable_unicode_literals_warning = True


@click.group()
def local():
    """
    Commands for local operations: train and deploy
    """
    pass


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.', help="Path to sagify module")
def train(dir):
    """
    Command to train ML model(s) locally
    """
    logger.info(ASCII_LOGO)
    logger.info("Started local training...\n")

    sagify_module_path = os.path.join(dir, 'sagify')
    local_train_script_path = os.path.join(sagify_module_path, 'local_test', 'train_local.sh')
    test_path = os.path.join(sagify_module_path, 'local_test', 'test_dir')

    if not os.path.isdir(test_path):
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)

    try:
        subprocess.check_output(
            [
                "{}".format(local_train_script_path),
                "{}".format(os.path.abspath(test_path))
            ]
        )

        logger.info("Local training completed successfully!")
    except Exception as e:
        logger.info("{}".format(e))
        return


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.', help="Path to sagify module")
def deploy(dir):
    """
    Command to deploy ML model(s) locally
    """
    logger.info(ASCII_LOGO)
    logger.info("Started local deployment at localhost:8080 ...\n")

    sagify_module_path = os.path.join(dir, 'sagify')
    local_deploy_script_path = os.path.join(sagify_module_path, 'local_test', 'deploy_local.sh')
    test_path = os.path.join(sagify_module_path, 'local_test', 'test_dir')

    if not os.path.isdir(test_path):
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)

    try:
        subprocess.check_output(
            [
                "{}".format(local_deploy_script_path),
                "{}".format(os.path.abspath(test_path))
            ]
        )
    except Exception as e:
        logger.info("{}".format(e))
        return


local.add_command(train)
local.add_command(deploy)
