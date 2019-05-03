# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os

from future.moves import subprocess

from sagify.log import logger


def push(dir, docker_tag, aws_region, iam_role_arn, aws_profile, external_id, image_name):
    """
    Push Docker image to AWS ECS

    :param dir: [str], source root directory
    :param docker_tag: [str], the Docker tag for the image
    :param aws_region: [str], the AWS region to push the image to
    :param iam_role_arn: [str], the AWS role used to push the image to ECR
    :param aws_profile: [str], the AWS profile used to push the image to ECR
    :param external_id: [str], Optional external id used when using an IAM role
    :param image_name: [str], The name of the Docker image
    """

    sagify_module_path = os.path.relpath(os.path.join(dir, 'sagify/'))
    push_script_path = os.path.join(sagify_module_path, 'push.sh')

    if not os.path.isfile(push_script_path):
        raise ValueError("This is not a sagify directory: {}".format(dir))

    output = subprocess.check_output([
                                     "{}".format(push_script_path),
                                     docker_tag,
                                     aws_region,
                                     iam_role_arn,
                                     aws_profile,
                                     external_id,
                                     image_name])
    logger.debug(output)
