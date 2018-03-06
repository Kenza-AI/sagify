import click

from sagify.log import logger


@click.command(name='create-endpoint')
def create_endpoint():
    logger.info("Let's create a SageMaker endpoint")
