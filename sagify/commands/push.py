# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys

import click

from sagify.api import push as api_push
from sagify.commands import ASCII_LOGO
from sagify.log import logger
from future.moves import subprocess

click.disable_unicode_literals_warning = True


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.', help="Path to sagify module")
@click.option(u"-p", u"--aws-profile", required=True, help="The AWS profile to use for the push command")
@click.pass_obj
def push(obj, dir, aws_profile):
    """
    Command to push Docker image to AWS ECS
    """
    logger.info(ASCII_LOGO)
    logger.info(
        "Started pushing Docker image to AWS ECS. It will take some time. Please, be patient...\n"
    )

    try:
        api_push.push(dir=dir, docker_tag=obj['docker_tag'], aws_profile=aws_profile)

        logger.info("Docker image pushed to ECS successfully!")
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except subprocess.CalledProcessError as e:
        logger.debug(e.output)
        raise
    except Exception as e:
        logger.info("{}".format(e))
        return
