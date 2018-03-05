import click

from sagify.log import logger


@click.command()
def configure():
    logger.info("Let's configure Sagify")
