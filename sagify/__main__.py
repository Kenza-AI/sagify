# -*- coding: utf-8 -*-
from __future__ import print_function

import click

from sagify.commands.build import build
from sagify.commands.cloud import cloud
from sagify.commands.initialize import init
from sagify.commands.local import local
from sagify.commands.push import push
from sagify.log import configure_logger


@click.group()
@click.option(u"-v", u"--verbose", count=True, help=u"Turn on debug logging")
@click.option(u"-t", u"--docker-tag", default=u"latest", help=u"Specify tag for Docker image")
@click.pass_context
def cli(ctx, verbose, docker_tag):
    """
    Sagify enables training and deploying machine learning models on AWS SageMaker in a few minutes!
    """
    configure_logger(verbose)
    ctx.obj = {'docker_tag': docker_tag}


def add_commands(cli):
    cli.add_command(init)
    cli.add_command(build)
    cli.add_command(local)
    cli.add_command(push)
    cli.add_command(cloud)


add_commands(cli)
