import click

from sagify.log import logger


@click.command()
@click.option(u"-d", u"--dir", required=False, default=None)
def init(dir):
    logger.info("Let's initialize Sagify")
