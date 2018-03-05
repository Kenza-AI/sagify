import click

from sagify.log import logger


@click.command()
def train():
    logger.info("Let's train a model on SageMaker")
