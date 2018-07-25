# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os

from future.moves import subprocess

from sagify.log import logger


def push(dir, docker_tag):
    """
    Push Docker image to AWS ECS

    :param dir: [str], source root directory
    """
    sagify_module_path = os.path.relpath(os.path.join(dir, 'sagify/'))

    push_script_path = os.path.join(sagify_module_path, 'push.sh')

    if not os.path.isfile(push_script_path):
        raise ValueError("This is not a sagify directory: {}".format(dir))

    output = subprocess.check_output(["{}".format(push_script_path), docker_tag])
    logger.debug(output)
