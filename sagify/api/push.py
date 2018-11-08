# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os

from future.moves import subprocess

from sagify.log import logger


def push(dir, docker_tag, aws_region, aws_profile):
    """
    Push Docker image to AWS ECS

    :param dir: [str], source root directory
    :param docker_tag: [str], the Docker tag for the image
    :param aws_region: [str], the AWS region to push the image to
    :param aws_profile: [str], the AWS profile used to push the image to ECR
    """
    sagify_module_path = os.path.relpath(os.path.join(dir, 'sagify/'))

    push_script_path = os.path.join(sagify_module_path, 'push.sh')

    if not os.path.isfile(push_script_path):
        raise ValueError("This is not a sagify directory: {}".format(dir))

    aws_region = "" if aws_region is None else aws_region
    aws_profile = "" if aws_profile is None else aws_profile
    output = subprocess.check_output(["{}".format(push_script_path), docker_tag, aws_region, aws_profile])
    logger.debug(output)
