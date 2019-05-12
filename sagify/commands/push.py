# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys

import click

from sagify.api import push as api_push
from sagify.commands import ASCII_LOGO
from sagify.log import logger
from future.moves import subprocess
from sagify.config.config import ConfigManager
import os

click.disable_unicode_literals_warning = True


@click.command()
@click.option(u"-r", u"--aws-region", required=False, help="The AWS region to push the image to")
@click.option(u"-i", u"--iam-role-arn", required=False, help="The AWS role to use for the push command")
@click.option(u"-p", u"--aws-profile", required=False, help="The AWS profile to use for the push command")
@click.option(u"-e", u"--external-id", required=False, help="Optional external id used when using an IAM role")
@click.pass_obj
def push(obj, aws_region, iam_role_arn, aws_profile, external_id):
    """
    Command to push Docker image to AWS ECS
    """
    logger.info(ASCII_LOGO)

    if iam_role_arn is not None and aws_profile is not None:
        logger.error('Only one of iam-role-arn and aws-profile can be used.')
        sys.exit(2)

    if iam_role_arn is not None:
        aws_profile = ''

    try:
        config_file_path = os.path.join('.sagify.json')
        if not os.path.isfile(config_file_path):
            raise ValueError()

        config = ConfigManager(config_file_path).get_config()
        image_name = config.image_name
        aws_region = config.aws_region if aws_region is None else aws_region
        aws_profile = config.aws_profile if (aws_profile is None and iam_role_arn is None) else aws_profile
        external_id = "" if external_id is None else external_id
        iam_role_arn = "" if iam_role_arn is None else iam_role_arn

        logger.info("Started pushing Docker image to AWS ECS. It will take some time. Please, be patient...\n")

        api_push.push(
            dir=config.sagify_module_dir,
            docker_tag=obj['docker_tag'],
            aws_region=aws_region,
            iam_role_arn=iam_role_arn,
            aws_profile=aws_profile,
            external_id=external_id,
            image_name=image_name)

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
