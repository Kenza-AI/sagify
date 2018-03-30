# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys

import click

from sagify.commands import ASCII_LOGO
from sagify.config.config import ConfigManager
from sagify.log import logger
from sagify.sagemaker import sagemaker


@click.group()
def cloud():
    """
    Commands for AWS operations: train and deploy
    """
    pass


@click.command(name='upload-data')
@click.option(u"-d", u"--dir", required=False, default='.')
@click.option(u"-i", u"--input-dir", required=True)
@click.option(u"-s", u"--s3-dir", required=True)
def upload_data(dir, input_dir, s3_dir):
    """
    Command to upload data to S3
    """
    logger.info(ASCII_LOGO)
    logger.info("Started uploading data to S3...\n")

    config_file_path = os.path.join(dir, 'sagify', 'config.json')
    if not os.path.isfile(config_file_path):
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)

    config = ConfigManager(config_file_path).get_config()
    sage_maker_client = sagemaker.SageMakerClient(config.aws_profile, config.aws_region)

    s3_path = sage_maker_client.upload_data(input_dir, s3_dir)

    logger.info("Data uploaded to {} successfully".format(s3_path))


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.')
@click.option(u"-n", u"--num-instances", required=True)
@click.option(u"-e", u"--ec2-type", required=True)
@click.option(u"-s", u"--s3-dir", required=True)
@click.option(u"-v", u"--volume-size", required=False, default=30)
@click.option(u"-t", u"--time-out", required=False, default=24 * 60 * 60)
def train(dir, num_instances, ec2_type, s3_dir, volume_size, time_out):
    """
    Command to train ML model(s) on SageMaker
    """
    logger.info(ASCII_LOGO)
    logger.info("Started training on SageMaker...\n")


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.')
@click.option(u"-n", u"--num-instances", required=True)
@click.option(u"-e", u"--ec2-type", required=True)
def deploy(dir, num_instances, ec2_type):
    """
    Command to deploy ML model(s) on SageMaker
    """
    logger.info(ASCII_LOGO)
    logger.info("Started deployment on SageMaker ...\n")


cloud.add_command(upload_data)
cloud.add_command(train)
cloud.add_command(deploy)
