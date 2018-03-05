import click

from sagify.log import logger


@click.command(name='upload-data')
def upload_data():
    logger.info("Let's upload data to S3")
