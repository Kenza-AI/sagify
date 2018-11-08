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
@click.option(u"-r", u"--aws-region", required=False, help="The AWS region to push the image to")
@click.option(u"-i", u"--iam-role-arn", required=False, help="The AWS role to use for the push command")
@click.option(u"-p", u"--aws-profile", required=False, help="The AWS profile to use for the push command")
@click.option(u"-e", u"--external-id", required=False, help="Optional external id used when using an IAM role")
@click.pass_obj
def push(obj, dir, aws_region, iam_role_arn, aws_profile, external_id):
    """
    Command to push Docker image to AWS ECS
    """
    logger.info(ASCII_LOGO)
    logger.info(
        "Started pushing Docker image to AWS ECS. It will take some time. Please, be patient...\n"
    )

    if iam_role_arn is not None and aws_profile is not None:
        logger.error('Only one of iam-role-arn and aws-profile can be used.')
        sys.exit(2)

    try:
        api_push.push(
            dir=dir,
            docker_tag=obj['docker_tag'],
            aws_region=aws_region,
            iam_role_arn=iam_role_arn,
            aws_profile=aws_profile,
            external_id=external_id)

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
