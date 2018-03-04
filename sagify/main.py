# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import click

from sagify.log import configure_logger


@click.group()
@click.option(u"-v", u"--verbose", count=True, help=u"Turn on debug logging")
def cli(verbose):
    """
    Sagify enables training and deploying machine learning models on AWS SageMaker in a few minutes!
    """
    configure_logger(verbose)
