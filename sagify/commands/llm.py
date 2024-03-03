# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import json
import pkg_resources
import os
import sys

import click
import docker

from sagify.api import cloud as api_cloud
from sagify.commands import ASCII_LOGO
from sagify.commands.custom_validators.validators import validate_tags
from sagify.log import logger
from sagify.sagemaker import sagemaker

click.disable_unicode_literals_warning = True


# Get the directory containing the Dockerfile
_DOCKERFILE_DIR = os.path.dirname(
    pkg_resources.resource_filename('sagify', 'Dockerfile')
)

OPENAI_BASE_URL = 'https://platform.openai.com'
OPENAI_DOCS = 'docs'
OPENAI_MODELS = 'models'
OPENAI_URL = f'{OPENAI_BASE_URL}/{OPENAI_DOCS}/{OPENAI_MODELS}'

ANTHROPIC_BASE_URL = 'https://docs.anthropic.com'
ANTHROPIC_DOCS = 'claude/reference'
ANTHROPIC_MODELS = 'models'
ANTHROPIC_URL = f'{ANTHROPIC_BASE_URL}/{ANTHROPIC_DOCS}/{ANTHROPIC_MODELS}'

HF_BASE_URL = 'https://huggingface.co'
HF_LLAMA = 'meta-llama'
HF_STABILITYAI = 'stabilityai'
HF_LLAMA_URL = f'{HF_BASE_URL}/{HF_LLAMA}'
HF_STABILITY_URL = f'{HF_BASE_URL}/{HF_STABILITYAI}'

VANTAGE_BASE_URL = 'https://instances.vantage.sh'
VANTAGE_AWS = 'aws'
VANTAGE_EC2 = 'ec2'
VANTAGE_URL = f'{VANTAGE_BASE_URL}/{VANTAGE_AWS}/{VANTAGE_EC2}'

_MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME = {
    'openai': {
        'gpt-4': ('gpt-4', f'{OPENAI_URL}/gpt-4-and-gpt-4-turbo'),
        'gpt-4-32k': ('gpt-4-32k', f'{OPENAI_URL}/gpt-4-and-gpt-4-turbo'),
        'gpt-3.5-turbo': ('gpt-3.5-turbo', f'{OPENAI_URL}/models/gpt-3-5-turbo'),
        'gpt-3.5-turbo-16k': ('gpt-3.5-turbo-16k', f'{OPENAI_URL}/gpt-3-5-turbo')
    },
    'sagemaker': {
        'llama-2-7b': ('meta-textgeneration-llama-2-7b-f', f'{HF_LLAMA_URL}/Llama-2-7b'),
        'llama-2-13b': ('meta-textgeneration-llama-2-13b-f', f'{HF_LLAMA_URL}/Llama-2-13b'),
        'llama-2-70b': ('meta-textgeneration-llama-2-70b-f', f'{HF_LLAMA_URL}/Llama-2-70b'),
    },
    'anthropic': {
        'claude-2.1': ('claude-2.1', ANTHROPIC_URL),
        'claude-2.0': ('claude-2.0', ANTHROPIC_URL),
        'claude-instant-1.2': ('claude-instant-1.2', ANTHROPIC_URL)
    }
}

_VALID_INSTANCE_TYPES_PER_CHAT_COMPLETIONS_MODEL = {
    'meta-textgeneration-llama-2-7b-f': [
        ('ml.g5.2xlarge', f'{VANTAGE_URL}/g5.2xlarge'),
        ('ml.g5.4xlarge', f'{VANTAGE_URL}/g5.4xlarge'),
        ('ml.g5.12xlarge', f'{VANTAGE_URL}/g5.12xlarge'),
        ('ml.g5.24xlarge', f'{VANTAGE_URL}/g5.24xlarge'),
        ('ml.g5.48xlarge', f'{VANTAGE_URL}/g5.48xlarge'),
        ('ml.p3dn.24xlarge', f'{VANTAGE_URL}/p3dn.24xlarge'),
    ],
    'meta-textgeneration-llama-2-13b-f': [
        ('ml.g5.12xlarge', f'{VANTAGE_URL}/g5.12xlarge'),
        ('ml.g5.24xlarge', f'{VANTAGE_URL}/g5.24xlarge'),
        ('ml.g5.48xlarge', f'{VANTAGE_URL}/g5.48xlarge'),
    ],
    'meta-textgeneration-llama-2-70b-f': [
        ('ml.g5.48xlarge', f'{VANTAGE_URL}/g5.48xlarge'),
    ],
}

_MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME = {
    'openai': {
        'dall-e-3': ('dall-e-3', f'{OPENAI_URL}/dall-e'),
        'dall-e-2': ('dall-e-2', f'{OPENAI_URL}/dall-e')
    },
    'sagemaker': {
        'stabilityai-stable-diffusion-v2': (
            'model-txt2img-stabilityai-stable-diffusion-v2',
            f'{HF_STABILITY_URL}/stable-diffusion-2'
        ),
        'stabilityai-stable-diffusion-v2-1-base': (
            'model-txt2img-stabilityai-stable-diffusion-v2-1-base',
            f'{HF_STABILITY_URL}/stable-diffusion-2-1-base'
        ),
        'stabilityai-stable-diffusion-v2-fp16': (
            'model-txt2img-stabilityai-stable-diffusion-v2-fp16',
            f'{HF_STABILITY_URL}/stable-diffusion-2/tree/fp16'
        )
    },
    'anthropic': {
        'NOT SUPPORTED': ('Learn more', ANTHROPIC_BASE_URL)
    }
}

_VALID_INSTANCE_TYPES_PER_IMAGE_CREATIONS_MODEL = {
    'model-txt2img-stabilityai-stable-diffusion-v2': [
        ('ml.p3.2xlarge', f'{VANTAGE_URL}/p3.2xlarge'),
        ('ml.g4dn.2xlarge', f'{VANTAGE_URL}/g4dn.2xlarge'),
        ('ml.g5.2xlarge', f'{VANTAGE_URL}/g5.2xlarge'),
    ],
    'model-txt2img-stabilityai-stable-diffusion-v2-1-base': [
        ('ml.p3.2xlarge', f'{VANTAGE_URL}/p3.2xlarge'),
        ('ml.g4dn.2xlarge', f'{VANTAGE_URL}/g4dn.2xlarge'),
        ('ml.g5.2xlarge', f'{VANTAGE_URL}/g5.2xlarge'),
    ],
    'model-txt2img-stabilityai-stable-diffusion-v2-fp16': [
        ('ml.p3.2xlarge', f'{VANTAGE_URL}/p3.2xlarge'),
        ('ml.g4dn.2xlarge', f'{VANTAGE_URL}/g4dn.2xlarge'),
        ('ml.g5.2xlarge', f'{VANTAGE_URL}/g5.2xlarge'),
    ],
}

_MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME = {
    'openai': {
        'text-embedding-3-large': ('text-embedding-3-large', f'{OPENAI_URL}/embeddings'),
        'text-embedding-3-small': ('text-embedding-3-small', f'{OPENAI_URL}/embeddings'),
        'text-embedding-ada-002': ('text-embedding-ada-002', f'{OPENAI_URL}/embeddings')
    },
    'sagemaker': {
        'bge-large-en': ('huggingface-sentencesimilarity-bge-large-en', 'https://huggingface.co/BAAI/bge-large-en'),
        'bge-base-en': ('huggingface-sentencesimilarity-bge-base-en', 'https://huggingface.co/BAAI/bge-base-en'),
        'gte-large': ('huggingface-sentencesimilarity-gte-large', 'https://huggingface.co/thenlper/gte-large'),
        'gte-base': ('huggingface-sentencesimilaritygte-base', 'https://huggingface.co/thenlper/gte-base'),
        'e5-large-v2': ('huggingface-sentencesimilarity-e5-large-v2', 'https://huggingface.co/intfloat/e5-large-v2'),
        'bge-small-en': ('huggingface-sentencesimilarity-bge-small-en', 'https://huggingface.co/BAAI/bge-small-en'),
        'e5-base-v2': ('huggingface-sentencesimilarity-e5-base-v2', 'https://huggingface.co/intfloat/e5-base-v2'),
        'multilingual-e5-large': ('huggingface-sentencesimilarity-multilingual-e5-large', 'https://huggingface.co/intfloat/multilingual-e5-large'),
        'e5-large': ('huggingface-sentencesimilarity-e5-large', 'https://huggingface.co/intfloat/e5-large'),
        'gte-small': ('huggingface-sentencesimilarity-gte-small', 'https://huggingface.co/thenlper/gte-small'),
        'e5-base': ('huggingface-sentencesimilarity-e5-base', 'https://huggingface.co/intfloat/e5-base'),
        'e5-small-v2': ('huggingface-sentencesimilarity-e5-small-v2', 'https://huggingface.co/intfloat/e5-small-v2'),
        'multilingual-e5-base': ('huggingface-sentencesimilarity-multilingual-e5-base', 'https://huggingface.co/intfloat/multilingual-e5-base'),
        'all-MiniLM-L6-v2': ('huggingface-sentencesimilarity-all-MiniLM-L6-v2', 'https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2'),
    },
    'anthropic': {
        'NOT SUPPORTED': ('Learn more', ANTHROPIC_BASE_URL)
    }

}

_VALID_EMBEDDINGS_INSTANCE_TYPES = [
    ('ml.g5.2xlarge', f'{VANTAGE_URL}/g5.2xlarge'),
    ('ml.g5.4xlarge', f'{VANTAGE_URL}/g5.4xlarge'),
    ('ml.g5.12xlarge', f'{VANTAGE_URL}/g5.12xlarge'),
    ('ml.g5.24xlarge', f'{VANTAGE_URL}/g5.24xlarge'),
    ('ml.g5.48xlarge', f'{VANTAGE_URL}/g5.48xlarge'),
    ('ml.p3dn.24xlarge', f'{VANTAGE_URL}/p3dn.24xlarge'),
    ('ml.p3.2xlarge', f'{VANTAGE_URL}/p3.2xlarge'),
    ('ml.p3.8xlarge', f'{VANTAGE_URL}/p3.8xlarge'),
    ('ml.p3.16xlarge', f'{VANTAGE_URL}/p3.16xlarge'),
]


@click.group()
def llm():
    """
    Commands for LLM (Large Language Model) operations
    """
    pass


@llm.command()
def platforms():
    """
    Commands to list supported platforms for LLM models
    """
    logger.info("Platforms:")
    logger.info(f"  - OpenAI: {OPENAI_BASE_URL}/{OPENAI_DOCS}/overview")
    logger.info(f"  - Anthropic: {ANTHROPIC_BASE_URL}")
    logger.info("  - AWS Sagemaker: https://aws.amazon.com/sagemaker")


@llm.command()
@click.option(
    '--all',
    is_flag=True,
    show_default=True,
    default=False,
    help='Show all LLM models.'
)
@click.option(
    '--chat-completions',
    is_flag=True,
    show_default=True,
    default=False,
    help='Show chat completions models.'
)
@click.option(
    '--image-creations',
    is_flag=True,
    show_default=True,
    default=False,
    help='Show image creations models.'
)
@click.option(
    '--embeddings',
    is_flag=True,
    show_default=True,
    default=False,
    help='Show embeddings models.'
)
@click.option(
    '--provider',
    type=str,
    show_default=True,
    default='sagemaker',
    help='Filter results by provider'
)
def models(all, chat_completions, image_creations, embeddings, provider):
    """
    Command to list available LLM models
    """
    logger.info(ASCII_LOGO)

    if not any([all, chat_completions, image_creations, embeddings]):
        logger.error("At least one of the flags --all, --chat-completions, --image-creations, --embeddings must be defined.")
        sys.exit(-1)

    if all:
        chat_completions, image_creations, embeddings = True, True, True

    if provider:
        chat_completions_mappings = {provider: _MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME[provider]}
        image_creation_mappings = {provider: _MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME[provider]}
        embeddings_mappings = {provider: _MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME[provider]}
    else:
        chat_completions_mappings = _MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME
        image_creation_mappings = _MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME
        embeddings_mappings = _MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME

    logger.info("Available LLM models:\n")

    if chat_completions:
        logger.info("Chat Completions:")
        for provider, provider_mappings in chat_completions_mappings.items():
            for model_id, (model_name, model_url) in provider_mappings.items():
                logger.info("  - Model: {}".format(model_id))
                logger.info("    Provider: {}".format(provider))
                logger.info("    Model URL: {}".format(model_url))
                if provider == 'sagemaker':
                    logger.info("    Instance Types:")
                    for instance_type, instance_url in _VALID_INSTANCE_TYPES_PER_CHAT_COMPLETIONS_MODEL[model_name]:
                        logger.info("      - Instance Type: {}".format(instance_type))
                        logger.info("        Instance URL: {}".format(instance_url))
            logger.info("\n")

    if image_creations:
        logger.info("Image Creations:")
        for provider, provider_mappings in image_creation_mappings.items():
            for model_id, (model_name, model_url) in provider_mappings.items():
                logger.info("  - Model: {}".format(model_id))
                logger.info("    Provider: {}".format(provider))
                logger.info("    Model URL: {}".format(model_url))
                if provider == 'sagemaker':
                    logger.info("    Instance Types:")
                    for instance_type, instance_url in _VALID_INSTANCE_TYPES_PER_IMAGE_CREATIONS_MODEL[model_name]:
                        logger.info("      - Instance Type: {}".format(instance_type))
                        logger.info("        Instance URL: {}".format(instance_url))
            logger.info("\n")

    if embeddings:
        logger.info("\nEmbeddings:")
        for provider, provider_mappings in embeddings_mappings.items():
            for model_id, (model_name, model_url) in provider_mappings.items():
                logger.info("  - Model: {}".format(model_id))
                logger.info("    Provider: {}".format(provider))
                logger.info("    Model URL: {}".format(model_url))
                if provider == 'sagemaker':
                    logger.info("    Instance Types:")
                    for instance_type, instance_url in _VALID_EMBEDDINGS_INSTANCE_TYPES:
                        logger.info("      - Instance Type: {}".format(instance_type))
                        logger.info("        Instance URL: {}".format(instance_url))


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
            'model': 'llama-2-7b',
            'instance_type': 'ml.g5.2xlarge',
            'num_instances': 1,
        },
        'image_creations': {
            'model': 'stabilityai-stable-diffusion-v2-1-base',
            'instance_type': 'ml.p3.2xlarge',
            'num_instances': 1,
        },
        'embeddings': {
            'model': 'gte-small',
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
            if default_config['chat_completions']['model'] not in _MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME['sagemaker']:
                raise ValueError(
                    "Invalid chat completions model id. Available model ids: {}".format(
                        list(_MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME['sagemaker'].keys())
                    )
                )

            instance_types = [
                item[0] for item in _VALID_INSTANCE_TYPES_PER_CHAT_COMPLETIONS_MODEL[
                    _MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME['sagemaker'][default_config['chat_completions']['model']][0]
                ]
            ]

            if default_config['chat_completions']['instance_type'] not in instance_types:
                raise ValueError(
                    "Invalid instance type for chat completions model. Available instance types: {}".format(
                        _VALID_INSTANCE_TYPES_PER_CHAT_COMPLETIONS_MODEL[
                            _MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME['sagemaker'][default_config['chat_completions']['model']][0]
                        ]
                    )
                )

            chat_endpoint_name, _ = api_cloud.foundation_model_deploy(
                model_id=_MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME['sagemaker'][default_config['chat_completions']['model']][0],
                model_version='1.*',
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
            if default_config['image_creations']['model'] not in _MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME['sagemaker']:
                raise ValueError(
                    "Invalid image creations model id. Available model ids: {}".format(
                        list(_MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME['sagemaker'].keys())
                    )
                )

            instance_types = [
                item[0] for item in _VALID_INSTANCE_TYPES_PER_IMAGE_CREATIONS_MODEL[
                    _MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME['sagemaker'][default_config['image_creations']['model']][0]
                ]
            ]

            if default_config['image_creations']['instance_type'] not in instance_types:
                raise ValueError(
                    "Invalid instance type for image creations model. Available instance types: {}".format(
                        _VALID_INSTANCE_TYPES_PER_IMAGE_CREATIONS_MODEL[
                            _MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME['sagemaker'][default_config['image_creations']['model']][0]
                        ]
                    )
                )

            image_endpoint_name, _ = api_cloud.foundation_model_deploy(
                model_id=_MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME['sagemaker'][default_config['image_creations']['model']][0],
                model_version='1.*',
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
            if default_config['embeddings']['model'] not in _MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME['sagemaker']:
                raise ValueError(
                    "Invalid embeddings model id. Available model ids: {}".format(
                        list(_MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME['sagemaker'].keys())
                    )
                )

            instance_types = [item[0] for item in _VALID_EMBEDDINGS_INSTANCE_TYPES]

            if default_config['embeddings']['instance_type'] not in instance_types:
                raise ValueError(
                    "Invalid instance type for embeddings model. Available instance types: {}".format(
                        _VALID_EMBEDDINGS_INSTANCE_TYPES
                    )
                )

            embeddings_endpoint_name, _ = api_cloud.foundation_model_deploy(
                model_id=_MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME['sagemaker'][default_config['embeddings']['model']][0],
                model_version='1.*',
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


@llm.command()
@click.option(
    u"--image",
    required=True,
    help="The docker image to run"
)
@click.option(
    '--start-local',
    is_flag=True,
    show_default=True,
    default=False,
    help='Start gateway locally'
)
@click.option(
    u"--platform",
    default="linux/amd64",
    required=False,
    help="The platform to use for the docker build"
)
def gateway(image, start_local, platform):
    """
    Command to build gateway docker image and start the gateway locally
    """
    logger.info(ASCII_LOGO)
    environment_vars = {
        'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY'),
        'ANTHROPIC_CHAT_COMPLETIONS_MODEL': os.environ.get('ANTHROPIC_CHAT_COMPLETIONS_MODEL'),
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        'OPENAI_CHAT_COMPLETIONS_MODEL': os.environ.get('OPENAI_CHAT_COMPLETIONS_MODEL'),
        'OPENAI_EMBEDDINGS_MODEL': os.environ.get('OPENAI_EMBEDDINGS_MODEL'),
        'OPENAI_IMAGE_CREATION_MODEL': os.environ.get('OPENAI_IMAGE_CREATION_MODEL'),
        'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION_NAME': os.environ.get('AWS_REGION_NAME'),
        'S3_BUCKET_NAME': os.environ.get('S3_BUCKET_NAME'),
        'SM_CHAT_COMPLETIONS_MODEL': os.environ.get('SM_CHAT_COMPLETIONS_MODEL'),
        'SM_EMBEDDINGS_MODEL': os.environ.get('SM_EMBEDDINGS_MODEL'),
        'SM_IMAGE_CREATION_MODEL': os.environ.get('SM_IMAGE_CREATION_MODEL'),
    }
    PORT = 8080
    client = docker.from_env()

    build_image = False
    try:
        client.images.get(image)
        build_image = False
        logger.info(f"Docker image: {image} exists. Skipping build...")
    except docker.errors.ImageNotFound:
        build_image = True
        logger.info(f"Docker image: {image} was not found")

    if build_image:
        logger.info("Building docker image...\n")

        image, build_logs = client.images.build(
            path=_DOCKERFILE_DIR,
            tag=image,
            rm=True,
            platform=platform,
            pull=True)
        for log in build_logs:
            logger.info(log)

    if start_local:
        logger.info("Starting local gateway...\n")
        container = client.containers.run(
            image=image,
            environment=environment_vars,
            ports={'8000/tcp': PORT},
            detach=True)
        logger.info(f"Local gateway started successfully. Container ID: {container.short_id}")
        logger.info(f"Access service docs: http://localhost:{PORT}/docs")


llm.add_command(platforms)
llm.add_command(models)
llm.add_command(start)
llm.add_command(stop)
llm.add_command(gateway)
