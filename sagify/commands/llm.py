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


_MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME = {
    'llama-2-7b': ('meta-textgeneration-llama-2-7b-f', 'https://huggingface.co/meta-llama/Llama-2-7b'),
    'llama-2-13b': ('meta-textgeneration-llama-2-13b-f', 'https://huggingface.co/meta-llama/Llama-2-13b'),
    'llama-2-70b': ('meta-textgeneration-llama-2-70b-f', 'https://huggingface.co/meta-llama/Llama-2-70b'),
}

_VALID_INSTANCE_TYPES_PER_CHAT_COMPLETIONS_MODEL = {
    'meta-textgeneration-llama-2-7b-f': [
        ('ml.g5.2xlarge', 'https://instances.vantage.sh/aws/ec2/g5.2xlarge'),
        ('ml.g5.4xlarge', 'https://instances.vantage.sh/aws/ec2/g5.4xlarge'),
        ('ml.g5.12xlarge', 'https://instances.vantage.sh/aws/ec2/g5.12xlarge'),
        ('ml.g5.24xlarge', 'https://instances.vantage.sh/aws/ec2/g5.24xlarge'),
        ('ml.g5.48xlarge', 'https://instances.vantage.sh/aws/ec2/g5.48xlarge'),
        ('ml.p3dn.24xlarge', 'https://instances.vantage.sh/aws/ec2/p3dn.24xlarge'),
    ],
    'meta-textgeneration-llama-2-13b-f': [
        ('ml.g5.12xlarge', 'https://instances.vantage.sh/aws/ec2/g5.12xlarge'),
        ('ml.g5.24xlarge', 'https://instances.vantage.sh/aws/ec2/g5.24xlarge'),
        ('ml.g5.48xlarge', 'https://instances.vantage.sh/aws/ec2/g5.48xlarge'),
    ],
    'meta-textgeneration-llama-2-70b-f': [
        ('ml.g5.48xlarge', 'https://instances.vantage.sh/aws/ec2/g5.48xlarge'),
    ],
}

_MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME = {
    'stabilityai-stable-diffusion-v2': (
        'model-txt2img-stabilityai-stable-diffusion-v2',
        'https://huggingface.co/stabilityai/stable-diffusion-2'
    ),
    'stabilityai-stable-diffusion-v2-1-base': (
        'model-txt2img-stabilityai-stable-diffusion-v2-1-base',
        'https://huggingface.co/stabilityai/stable-diffusion-2-1-base'
    ),
    'stabilityai-stable-diffusion-v2-fp16': (
        'model-txt2img-stabilityai-stable-diffusion-v2-fp16',
        'https://huggingface.co/stabilityai/stable-diffusion-2/tree/fp16'
    )
}

_VALID_INSTANCE_TYPES_PER_IMAGE_CREATIONS_MODEL = {
    'model-txt2img-stabilityai-stable-diffusion-v2': [
        ('ml.p3.2xlarge', 'https://instances.vantage.sh/aws/ec2/p3.2xlarge'),
        ('ml.g4dn.2xlarge', 'https://instances.vantage.sh/aws/ec2/g4dn.2xlarge'),
        ('ml.g5.2xlarge', 'https://instances.vantage.sh/aws/ec2/g5.2xlarge'),
    ],
    'model-txt2img-stabilityai-stable-diffusion-v2-1-base': [
        ('ml.p3.2xlarge', 'https://instances.vantage.sh/aws/ec2/p3.2xlarge'),
        ('ml.g4dn.2xlarge', 'https://instances.vantage.sh/aws/ec2/g4dn.2xlarge'),
        ('ml.g5.2xlarge', 'https://instances.vantage.sh/aws/ec2/g5.2xlarge'),
    ],
    'model-txt2img-stabilityai-stable-diffusion-v2-fp16': [
        ('ml.p3.2xlarge', 'https://instances.vantage.sh/aws/ec2/p3.2xlarge'),
        ('ml.g4dn.2xlarge', 'https://instances.vantage.sh/aws/ec2/g4dn.2xlarge'),
        ('ml.g5.2xlarge', 'https://instances.vantage.sh/aws/ec2/g5.2xlarge'),
    ],
}

_MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME = {
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
}

_VALID_EMBEDDINGS_INSTANCE_TYPES = [
    ('ml.g5.2xlarge', 'https://instances.vantage.sh/aws/ec2/g5.2xlarge'),
    ('ml.g5.4xlarge', 'https://instances.vantage.sh/aws/ec2/g5.4xlarge'),
    ('ml.g5.12xlarge', 'https://instances.vantage.sh/aws/ec2/g5.12xlarge'),
    ('ml.g5.24xlarge', 'https://instances.vantage.sh/aws/ec2/g5.24xlarge'),
    ('ml.g5.48xlarge', 'https://instances.vantage.sh/aws/ec2/g5.48xlarge'),
    ('ml.p3dn.24xlarge', 'https://instances.vantage.sh/aws/ec2/p3dn.24xlarge'),
    ('ml.p3.2xlarge', 'https://instances.vantage.sh/aws/ec2/p3.2xlarge'),
    ('ml.p3.8xlarge', 'https://instances.vantage.sh/aws/ec2/p3.8xlarge'),
    ('ml.p3.16xlarge', 'https://instances.vantage.sh/aws/ec2/p3.16xlarge'),
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
    logger.info("  - OpenAI: https://platform.openai.com/docs/overview")
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
def sagemaker_models(all, chat_completions, image_creations, embeddings):
    """
    Command to list available LLM models
    """
    logger.info(ASCII_LOGO)

    if not any([all, chat_completions, image_creations, embeddings]):
        logger.error("At least one of the flags --all, --chat-completions, --image-creations, --embeddings must be defined.")
        sys.exit(-1)

    if all:
        chat_completions, image_creations, embeddings = True, True, True

    logger.info("Available LLM models:\n")

    if chat_completions:
        logger.info("Chat Completions:")
        for model_id, (model_name, model_url) in _MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME.items():
            logger.info("  - Model: {}".format(model_id))
            logger.info("    Model URL: {}".format(model_url))
            logger.info("    Instance Types:")
            for instance_type, instance_url in _VALID_INSTANCE_TYPES_PER_CHAT_COMPLETIONS_MODEL[model_name]:
                logger.info("      - Instance Type: {}".format(instance_type))
                logger.info("        Instance URL: {}".format(instance_url))
        logger.info("\n")

    if image_creations:
        logger.info("Image Creations:")
        for model_id, (model_name, model_url) in _MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME.items():
            logger.info("  - Model: {}".format(model_id))
            logger.info("    Model URL: {}".format(model_url))
            logger.info("    Instance Types:")
            for instance_type, instance_url in _VALID_INSTANCE_TYPES_PER_IMAGE_CREATIONS_MODEL[model_name]:
                logger.info("      - Instance Type: {}".format(instance_type))
                logger.info("        Instance URL: {}".format(instance_url))
        logger.info("\n")

    if embeddings:
        logger.info("\nEmbeddings:")
        for model_id, (model_name, model_url) in _MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME.items():
            logger.info("  - Model: {}".format(model_id))
            logger.info("    Model URL: {}".format(model_url))
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
            if default_config['chat_completions']['model'] not in _MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME:
                raise ValueError(
                    "Invalid chat completions model id. Available model ids: {}".format(
                        list(_MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME.keys())
                    )
                )
            
            instance_types = [
                item[0] for item in _VALID_INSTANCE_TYPES_PER_CHAT_COMPLETIONS_MODEL[
                    _MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME[default_config['chat_completions']['model']][0]
                ]
            ]

            if default_config['chat_completions']['instance_type'] not in instance_types:
                raise ValueError(
                    "Invalid instance type for chat completions model. Available instance types: {}".format(
                        _VALID_INSTANCE_TYPES_PER_CHAT_COMPLETIONS_MODEL[
                            _MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME[default_config['chat_completions']['model']][0]
                        ]
                    )
                )

            chat_endpoint_name, _ = api_cloud.foundation_model_deploy(
                model_id=_MAPPING_CHAT_COMPLETIONS_MODEL_ID_TO_MODEL_NAME[default_config['chat_completions']['model']][0],
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
            if default_config['image_creations']['model'] not in _MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME:
                raise ValueError(
                    "Invalid image creations model id. Available model ids: {}".format(
                        list(_MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME.keys())
                    )
                )
            
            instance_types = [
                item[0] for item in _VALID_INSTANCE_TYPES_PER_IMAGE_CREATIONS_MODEL[
                    _MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME[default_config['image_creations']['model']][0]
                ]
            ]

            if default_config['image_creations']['instance_type'] not in instance_types:
                raise ValueError(
                    "Invalid instance type for image creations model. Available instance types: {}".format(
                        _VALID_INSTANCE_TYPES_PER_IMAGE_CREATIONS_MODEL[
                            _MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME[default_config['image_creations']['model']][0]
                        ]
                    )
                )

            image_endpoint_name, _ = api_cloud.foundation_model_deploy(
                model_id=_MAPPING_IMAGE_CREATION_MODEL_ID_TO_MODEL_NAME[default_config['image_creations']['model']][0],
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
            if default_config['embeddings']['model'] not in _MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME:
                raise ValueError(
                    "Invalid embeddings model id. Available model ids: {}".format(
                        list(_MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME.keys())
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
                model_id=_MAPPING_EMBEDDINGS_MODEL_ID_TO_MODEL_NAME[default_config['embeddings']['model']][0],
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
def start_local_gateway():
    """
    Command to start local gateway
    """
    logger.info(ASCII_LOGO)
    logger.info("Starting local gateway...\n")
    from sagify.llm_gateway.main import start_server
    start_server()


llm.add_command(platforms)
llm.add_command(sagemaker_models)
llm.add_command(start)
llm.add_command(stop)
