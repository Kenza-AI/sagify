# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys

import boto3
import click
from click import BadParameter

from sagify.api import initialize as api_initialize
from sagify.commands import ASCII_LOGO
from sagify.log import logger

click.disable_unicode_literals_warning = True


_FILE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def _get_local_aws_profiles():
    return boto3.Session().available_profiles


def ask_for_app_name():
    return click.prompt(
        text="Type in a name for your SageMaker app (Only alphanumeric characters and - are allowed))",
        type=str
    )


def ask_if_existing_project_exists():
    return click.confirm(text="Are you starting a new project?")


def ask_for_root_dir():
    return click.prompt(text="Type in the directory where your code lives. Example: src", type=str).strip('/')


def ask_for_python_version():
    logger.info("Select Python interpreter:")
    logger.info('{}'.format('\n'.join(['1 - Python37', '2 - Python38'])))

    def _validate_python_option(input_value):
        if int(input_value) not in {1, 2}:
            raise BadParameter(
                message="invalid choice: {}. (choose from 1, 2)".format(str(input_value))
            )

        return int(input_value)

    chosen_python_index = click.prompt(
        text="Choose from 1, 2",
        default=1,
        value_proc=lambda x: _validate_python_option(x)
    )

    return '3.7' if chosen_python_index == 1 else '3.8'


def ask_for_aws_details():
    available_profiles = _get_local_aws_profiles()

    if len(available_profiles) == 0:
        logger.info("aws cli is not configured!")
        return

    valid_positions = list(range(1, len(available_profiles) + 1))
    logger.info("Select AWS profile:")
    logger.info('{}'.format(
            '\n'.join(
                [
                    '{} - {}'.format(pos, profile)
                    for pos, profile in zip(valid_positions, available_profiles)
                ]
            )
        )
    )

    def _validate_profile_position(input_pos):
        if int(input_pos) not in valid_positions:
            raise BadParameter(
                message="invalid choice: {}. (choose from {})".format(
                    input_pos,
                    ', '.join([str(pos) for pos in valid_positions])
                )
            )
        return int(input_pos)

    chosen_profile_index = click.prompt(
        text="Choose from {}".format(', '.join([str(pos) for pos in valid_positions])),
        default=1,
        value_proc=lambda x: _validate_profile_position(x)
    )
    chosen_profile_index -= 1

    chosen_profile = available_profiles[chosen_profile_index]

    chosen_region = click.prompt(
        text="Type in your preferred AWS region name",
        default='us-east-1',
        type=str
    )

    return chosen_profile, chosen_region


def ask_for_requirements_dir():
    return click.prompt(text="Type in the path to requirements.txt. Example: requirements.txt", type=str).strip('/')


@click.command()
def init():
    """
    Command to initialize SageMaker template
    """
    logger.info(ASCII_LOGO)

    sagify_app_name = ask_for_app_name()

    is_new_project = ask_if_existing_project_exists()

    root_dir = None
    if not is_new_project:
        root_dir = ask_for_root_dir()

    python_version = ask_for_python_version()

    aws_profile, aws_region = ask_for_aws_details()

    requirements_dir = ask_for_requirements_dir()

    try:
        api_initialize.init(
            sagify_app_name=sagify_app_name,
            aws_profile=aws_profile,
            aws_region=aws_region,
            python_version=python_version,
            root_dir=root_dir if root_dir else 'src',
            requirements_dir=requirements_dir
        )

        logger.info("\nsagify module is created! ヽ(´▽`)/")
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)
