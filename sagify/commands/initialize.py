# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
import sys

import boto3
import click
from click import BadParameter
from cookiecutter.main import cookiecutter

from sagify.commands import ASCII_LOGO
from sagify.log import logger

click.disable_unicode_literals_warning = True


_FILE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def _get_local_aws_profiles():
    return boto3.Session().available_profiles


def ask_for_app_name():
    return click.prompt(text="Type in a name for your SageMaker app", type=str)


def ask_for_python_version():
    logger.info("Select Python interpreter:")
    logger.info('{}'.format('\n'.join(['1 - Python3', '2 - Python2'])))

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

    return '3.6' if chosen_python_index == 1 else '2.7'


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
        return int(input_pos) - 1

    chosen_profile_index = click.prompt(
        text="Choose from {}".format(', '.join([str(pos) for pos in valid_positions])),
        default=1,
        value_proc=lambda x: _validate_profile_position(x)
    )

    chosen_profile = available_profiles[chosen_profile_index]

    chosen_region = click.prompt(
        text="Type in your preferred AWS region name",
        default='us-east-1',
        type=str
    )

    return chosen_profile, chosen_region


def template_creation(app_name, aws_profile, aws_region, python_version, output_dir):
    sagify_module_name = 'sagify'

    sagify_exists = os.path.exists(os.path.join(output_dir, sagify_module_name))
    if sagify_exists:
        logger.info("There is a sagify directory/module already. "
                    "Please, rename it in order to use sagify."
                    )
        sys.exit(-1)

    Path(output_dir).mkdir(exist_ok=True)
    Path(os.path.join(output_dir, '__init__.py')).touch()

    cookiecutter(
        template=os.path.join(_FILE_DIR_PATH, '../template/'),
        output_dir=output_dir,
        no_input=True,
        extra_context={
            "project_slug": app_name,
            "module_slug": sagify_module_name,
            "aws_profile": aws_profile,
            "aws_region": aws_region,
            "python_version": python_version
        }
    )


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.', help="Path to create sagify module")
def init(dir):
    """
    Command to initialize SageMaker template
    """
    logger.info(ASCII_LOGO)

    sagify_app_name = ask_for_app_name()

    python_version = ask_for_python_version()

    aws_profile, aws_region = ask_for_aws_details()

    template_creation(
        app_name=sagify_app_name,
        aws_profile=aws_profile,
        aws_region=aws_region,
        python_version=python_version,
        output_dir=dir
    )

    logger.info("\nsagify module is created! ヽ(´▽`)/")
