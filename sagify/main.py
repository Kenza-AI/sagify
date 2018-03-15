# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import click

from sagify.commands.create_endpoint import create_endpoint
from sagify.commands.initialize import init
from sagify.commands.train import train
from sagify.commands.upload_data import upload_data
from sagify.log import configure_logger


@click.group()
@click.option(u"-v", u"--verbose", count=True, help=u"Turn on debug logging")
def cli(verbose):
    """
    Sagify enables training and deploying machine learning models on AWS SageMaker in a few minutes!
    """
    configure_logger(verbose)


def add_commands(cli):
    cli.add_command(init)
    cli.add_command(create_endpoint)
    cli.add_command(train)
    cli.add_command(upload_data)


add_commands(cli)
