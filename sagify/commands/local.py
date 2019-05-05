# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys
import click

from sagify.api import local as api_local
from sagify.commands import ASCII_LOGO
from sagify.log import logger
from future.moves import subprocess
from sagify.config.config import ConfigManager

click.disable_unicode_literals_warning = True


@click.group()
def local():
    """
    Commands for local operations: train and deploy
    """
    pass


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.', help="Path to sagify module")
@click.pass_obj
def train(obj, dir):
    """
    Command to train ML model(s) locally
    """
    logger.info(ASCII_LOGO)
    logger.info("Started local training...\n")

    try:
        config = ConfigManager(os.path.join(dir, 'sagify', 'config.json')).get_config()
        api_local.train(dir=dir, docker_tag=obj['docker_tag'], image_name=config.image_name)

        logger.info("Local training completed successfully!")
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except subprocess.CalledProcessError as e:
        logger.debug(e.output)
        raise
    except Exception as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.', help="Path to sagify module")
@click.pass_obj
def deploy(obj, dir):
    """
    Command to deploy ML model(s) locally
    """
    logger.info(ASCII_LOGO)
    logger.info("Started local deployment at localhost:8080 ...\n")

    try:
        config = ConfigManager(os.path.join(dir, 'sagify', 'config.json')).get_config()
        api_local.deploy(dir=dir, docker_tag=obj['docker_tag'], image_name=config.image_name)
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except subprocess.CalledProcessError as e:
        logger.debug(e.output)
        raise
    except Exception as e:
        logger.info("{}".format(e))
        sys.exit(-1)


local.add_command(train)
local.add_command(deploy)
