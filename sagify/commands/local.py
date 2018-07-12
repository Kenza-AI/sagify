# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys

import click

from sagify.api import local as api_local
from sagify.commands import ASCII_LOGO
from sagify.log import logger
from future.moves import subprocess

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
        api_local.train(dir=dir, docker_tag=obj['docker_tag'])

        logger.info("Local training completed successfully!")
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except subprocess.CalledProcessError as e:
        logger.debug(e.output)
        raise
    except Exception as e:
        logger.info("{}".format(e))
        return


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
        api_local.deploy(dir=dir, docker_tag=obj['docker_tag'])
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except subprocess.CalledProcessError as e:
        logger.debug(e.output)
        raise
    except Exception as e:
        logger.info("{}".format(e))
        return


local.add_command(train)
local.add_command(deploy)
