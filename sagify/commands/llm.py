# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import json
import sys

import click

from sagify.api import cloud as api_cloud
from sagify.commands import ASCII_LOGO
from sagify.commands.custom_validators.validators import validate_tags
from sagify.log import logger
from sagify.sagemaker import sagemaker

click.disable_unicode_literals_warning = True


@click.group()
def llm():
    """
    Commands for LLM (Large Language Model) operations
    """
    pass


@llm.command()
@click.option(
    '--all',
    is_flag=True,
    show_default=True,
    default=False,
    help='Start infrastructure for all services.'
)
@click.option(
    '--chat-completions',
    is_flag=True,
    show_default=True,
    default=False,
    help='Start infrastructure for chat completions.'
)
@click.option(
    '--image-creations',
    is_flag=True,
    show_default=True,
    default=False,
    help='Start infrastructure for image creations.'
)
@click.option(
    '--embeddings',
    is_flag=True,
    show_default=True,
    default=False,
    help='Start infrastructure for embeddings.'
)
@click.option('--config', required=False, type=click.File('r'), help='Path to config file.')
@click.option(
    u"-a", u"--aws-tags",
    callback=validate_tags,
    required=False,
    default=None,
    help='Tags for labeling a training job of the form "tag1=value1;tag2=value2". For more, see '
         'https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.'
)
@click.option(
    u"--aws-profile",
    required=True,
    help="The AWS profile to use for the foundation model deploy command"
)
@click.option(
    u"--aws-region",
    required=True,
    help="The AWS region to use for the foundation model deploy command"
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for the foundation model deploy command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
def start(
        all,
        chat_completions,
        image_creations,
        embeddings,
        config,
        aws_tags,
        aws_profile,
        aws_region,
        iam_role_arn,
        external_id
):
    """
    Command to start LLM infrastructure
    """
    logger.info(ASCII_LOGO)
    logger.info("Starting LLM infrastructure. It will take ~15-30 mins...\n")

    # Default configuration
    default_config = {
        'chat_completions': {
            'model': 'meta-textgeneration-llama-2-7b-f',
            'model_version': '1.*',
            'instance_type': 'ml.g5.2xlarge',
            'num_instances': 1,
        },
        'image_creations': {
            'model': 'model-txt2img-stabilityai-stable-diffusion-v2-1-base',
            'model_version': '1.*',
            'instance_type': 'ml.p3.2xlarge',
            'num_instances': 1,
        },
        'embeddings': {
            'model': 'huggingface-sentencesimilarity-gte-small',
            'model_version': '1.*',
            'instance_type': 'ml.g5.2xlarge',
            'num_instances': 1,
        },
    }

    # Load the config file if provided
    if config:
        custom_config = json.load(config)
        default_config.update(custom_config)

    try:
        if all:
            chat_completions, image_creations, embeddings = True, True, True

        llm_infra_config = {
            'chat_completions_endpoint': None,
            'image_creations_endpoint': None,
            'embeddings_endpoint': None,
        }

        if chat_completions:
            chat_endpoint_name, _ = api_cloud.foundation_model_deploy(
                model_id=default_config['chat_completions']['model'],
                model_version=default_config['chat_completions']['model_version'],
                num_instances=default_config['chat_completions']['num_instances'],
                ec2_type=default_config['chat_completions']['instance_type'],
                aws_region=aws_region,
                aws_profile=aws_profile,
                aws_role=iam_role_arn,
                external_id=external_id,
                tags=aws_tags
            )
            llm_infra_config['chat_completions_endpoint'] = chat_endpoint_name

            logger.info("Chat Completions Endpoint Name: {}".format(chat_endpoint_name))

        if image_creations:
            image_endpoint_name, _ = api_cloud.foundation_model_deploy(
                model_id=default_config['image_creations']['model'],
                model_version=default_config['image_creations']['model_version'],
                num_instances=default_config['image_creations']['num_instances'],
                ec2_type=default_config['image_creations']['instance_type'],
                aws_region=aws_region,
                aws_profile=aws_profile,
                aws_role=iam_role_arn,
                external_id=external_id,
                tags=aws_tags
            )
            llm_infra_config['image_creations_endpoint'] = image_endpoint_name

            logger.info("Image Creations Endpoint Name: {}".format(image_endpoint_name))

        if embeddings:
            embeddings_endpoint_name, _ = api_cloud.foundation_model_deploy(
                model_id=default_config['embeddings']['model'],
                model_version=default_config['embeddings']['model_version'],
                num_instances=default_config['embeddings']['num_instances'],
                ec2_type=default_config['embeddings']['instance_type'],
                aws_region=aws_region,
                aws_profile=aws_profile,
                aws_role=iam_role_arn,
                external_id=external_id,
                tags=aws_tags
            )
            llm_infra_config['embeddings_endpoint'] = embeddings_endpoint_name

            logger.info("Embeddings Endpoint Name: {}".format(embeddings_endpoint_name))

        with open('.sagify_llm_infra.json', 'w') as f:
            json.dump(llm_infra_config, f)
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command()
@click.option(
    '--all',
    is_flag=True,
    show_default=True,
    default=False,
    help='Start infrastructure for all services.'
)
@click.option(
    '--chat-completions',
    is_flag=True,
    show_default=True,
    default=False,
    help='Start infrastructure for chat completions.'
)
@click.option(
    '--image-creations',
    is_flag=True,
    show_default=True,
    default=False,
    help='Start infrastructure for image creations.'
)
@click.option(
    '--embeddings',
    is_flag=True,
    show_default=True,
    default=False,
    help='Start infrastructure for embeddings.'
)
@click.option(
    u"--aws-profile",
    required=True,
    help="The AWS profile to use for the foundation model deploy command"
)
@click.option(
    u"--aws-region",
    required=True,
    help="The AWS region to use for the foundation model deploy command"
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for the train command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
def stop(
    all,
    chat_completions,
    image_creations,
    embeddings,
    aws_profile,
    aws_region,
    iam_role_arn,
    external_id
):
    """
    Command to stop LLM infrastructure
    """
    logger.info(ASCII_LOGO)
    logger.info("Stopping LLM infrastructure...\n")

    sagemaker_client = sagemaker.SageMakerClient(aws_profile, aws_region, iam_role_arn, external_id)
    try:
        with open('.sagify_llm_infra.json', 'r') as f:
            llm_infra_config = json.load(f)

        endpoints_to_stop = []
        if all:
            endpoints_to_stop = ['chat_completions_endpoint', 'image_creations_endpoint', 'embeddings_endpoint']
        else:
            if chat_completions:
                endpoints_to_stop.append('chat_completions_endpoint')
            if image_creations:
                endpoints_to_stop.append('image_creations_endpoint')
            if embeddings:
                endpoints_to_stop.append('embeddings_endpoint')

        for _endpoint in endpoints_to_stop:
            if llm_infra_config[_endpoint]:
                try:
                    sagemaker_client.shutdown_endpoint(llm_infra_config[_endpoint])
                except Exception as e:
                    logger.info("{}".format(e))
                    sys.exit(-1)

        logger.info("LLM infrastructure stopped successfully.")
    except FileNotFoundError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


llm.add_command(start)
llm.add_command(stop)
