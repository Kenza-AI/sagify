# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys

import click

from sagify.api import cloud as api_cloud
from sagify.commands import ASCII_LOGO
from sagify.commands.custom_validators.validators import validate_tags
from sagify.log import logger
from sagify.config.config import ConfigManager

click.disable_unicode_literals_warning = True


def _config():
    return ConfigManager('.sagify.json').get_config()


@click.group()
def cloud():
    """
    Commands for AWS operations: upload data, train and deploy
    """
    pass


@click.command(name='upload-data')
@click.option(u"-i", u"--input-dir", required=True, help="Path to data input directory")
@click.option(
    u"-s", u"--s3-dir",
    required=True,
    help="s3 location to upload data",
    type=click.Path()
)
def upload_data(input_dir, s3_dir):
    """
    Command to upload data to S3
    """
    logger.info(ASCII_LOGO)
    logger.info("Started uploading data to S3...\n")

    try:
        s3_path = api_cloud.upload_data(
            dir=_config().sagify_module_dir,
            input_dir=input_dir,
            s3_dir=s3_dir
        )

        logger.info("Data uploaded to {} successfully".format(s3_path))
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command()
@click.option(
    u"-i", u"--input-s3-dir",
    required=True,
    help="s3 location to input data",
    type=click.Path()
)
@click.option(
    u"-o", u"--output-s3-dir",
    required=True,
    help="s3 location to save output (models, etc)",
    type=click.Path()
)
@click.option(
    u"-h", u"--hyperparams-file",
    required=False,
    help="Path to hyperparams file",
    type=click.Path(resolve_path=True)
)
@click.option(u"-e", u"--ec2-type", required=True, help="ec2 instance type")
@click.option(
    u"-v", u"--volume-size",
    required=False,
    default=30,
    help="size in GB of the EBS volume (default: 30)"
)
@click.option(
    u"-s", u"--time-out",
    required=False,
    default=24 * 60 * 60,
    help="time-out in seconds (default: 24 * 60 * 60)"
)
@click.option(
    u"-a", u"--aws-tags",
    callback=validate_tags,
    required=False,
    default=None,
    help='Tags for labeling a training job of the form "tag1=value1;tag2=value2". For more, see '
         'https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.'
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for the push command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
@click.option(
    u"-n",
    u"--base-job-name",
    required=False,
    help="Optional prefix for the SageMaker training job."
    "If not specified, the estimator generates a default job name, based on the training image name and current timestamp."
)
@click.option(
    u"--job-name",
    required=False,
    help="Optional name for the SageMaker training job."
    "NOTE: if a `--base-job-name` is passed along with this option, it will be ignored."
)
@click.option(
    u"--metric-names",
    required=False,
    default=None,
    help='Optional comma-separated metric names for tracking performance of training jobs. Example: Precision,Recall,AUC '
)
@click.pass_obj
def train(
        obj,
        input_s3_dir,
        output_s3_dir,
        hyperparams_file,
        ec2_type,
        volume_size,
        time_out,
        aws_tags,
        iam_role_arn,
        external_id,
        base_job_name,
        job_name,
        metric_names
):
    """
    Command to train ML model(s) on SageMaker
    """
    logger.info(ASCII_LOGO)
    logger.info("Started training on SageMaker...\n")

    try:
        s3_model_location = api_cloud.train(
            dir=_config().sagify_module_dir,
            input_s3_dir=input_s3_dir,
            output_s3_dir=output_s3_dir,
            hyperparams_file=hyperparams_file,
            ec2_type=ec2_type,
            volume_size=volume_size,
            time_out=time_out,
            docker_tag=obj['docker_tag'],
            tags=aws_tags,
            aws_role=iam_role_arn,
            external_id=external_id,
            base_job_name=base_job_name,
            job_name=job_name,
            metric_names=[_val.strip() for _val in metric_names.split(',')] if metric_names else None
        )

        logger.info("Training on SageMaker succeeded")
        logger.info("Model S3 location: {}".format(s3_model_location))
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command()
@click.option(
    u"-i", u"--input-s3-dir",
    required=True,
    help="s3 location to input data",
    type=click.Path()
)
@click.option(
    u"-o", u"--output-s3-dir",
    required=True,
    help="s3 location to save the multiple trained models",
    type=click.Path()
)
@click.option(
    u"-h", u"--hyperparams-config-file",
    required=True,
    help="Local path to hyperparameters configuration file",
    type=click.Path(resolve_path=True)
)
@click.option(u"-e", u"--ec2-type", required=True, help="ec2 instance type")
@click.option(
    u"-m", u"--max-jobs",
    required=False,
    default=3,
    help="Maximum total number of training jobs to start for the hyperparameter tuning job (default: 3)"
)
@click.option(
    u"-p", u"--max-parallel-jobs",
    required=False,
    default=1,
    help="Maximum number of parallel training jobs to start (default: 1)"
)
@click.option(
    u"-v", u"--volume-size",
    required=False,
    default=30,
    help="size in GB of the EBS volume (default: 30)"
)
@click.option(
    u"-s", u"--time-out",
    required=False,
    default=24 * 60 * 60,
    help="time-out in seconds (default: 24 * 60 * 60)"
)
@click.option(
    u"-a", u"--aws-tags",
    callback=validate_tags,
    required=False,
    default=None,
    help='Tags for labeling a training job of the form "tag1=value1;tag2=value2". For more, see '
         'https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.'
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for the push command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
@click.option(
    u"-n",
    u"--base-job-name",
    required=False,
    help="Optional prefix for the SageMaker training job."
    "If not specified, the estimator generates a default job name, "
    "based on the training image name and current timestamp."
)
@click.option(
    u"--job-name",
    required=False,
    help="Optional name for the SageMaker tuning job."
    "NOTE: if a `--base-job-name` is passed along with this option, it will be ignored."
)
@click.option(
    u"-w",
    u"--wait",
    default=False,
    is_flag=True,
    help="Wait until Hyperparameter Tuning is finished. "
         "Default: don't wait"
)
@click.pass_obj
def hyperparameter_optimization(
        obj,
        input_s3_dir,
        output_s3_dir,
        hyperparams_config_file,
        ec2_type,
        max_jobs,
        max_parallel_jobs,
        volume_size,
        time_out,
        aws_tags,
        iam_role_arn,
        external_id,
        base_job_name,
        job_name,
        wait
):
    """
    Command for hyperparameter optimization on SageMaker
    """
    logger.info(ASCII_LOGO)
    logger.info("Started hyperparameter optimization on SageMaker...\n")

    try:
        best_job_name = api_cloud.hyperparameter_optimization(
            dir=_config().sagify_module_dir,
            input_s3_dir=input_s3_dir,
            output_s3_dir=output_s3_dir,
            hyperparams_config_file=hyperparams_config_file,
            ec2_type=ec2_type,
            max_jobs=max_jobs,
            max_parallel_jobs=max_parallel_jobs,
            volume_size=volume_size,
            time_out=time_out,
            docker_tag=obj['docker_tag'],
            tags=aws_tags,
            aws_role=iam_role_arn,
            external_id=external_id,
            base_job_name=base_job_name,
            job_name=job_name,
            wait=wait
        )

        logger.info("Hyperparameter Optimization on SageMaker started successfully")
        if best_job_name:
            logger.info("Best job name: {}".format(best_job_name))
        else:
            logger.info(
                "Hypeparameter Optimization takes time. "
                "Please, go to SageMaker UI console to retrieve the status of this tuning job."
            )
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command()
@click.option(
    u"-m", u"--s3-model-location",
    required=True,
    help="s3 location to model tar.gz",
    type=click.Path()
)
@click.option(u"-n", u"--num-instances", required=True, type=int, help="Number of ec2 instances")
@click.option(u"-e", u"--ec2-type", required=True, help="ec2 instance type")
@click.option(
    u"-a", u"--aws-tags",
    callback=validate_tags,
    required=False,
    default=None,
    help='Tags for labeling a training job of the form "tag1=value1;tag2=value2". For more, see '
         'https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.'
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for the push command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
@click.pass_obj
def deploy(obj, s3_model_location, num_instances, ec2_type, aws_tags, iam_role_arn, external_id):
    """
    Command to deploy ML model(s) on SageMaker
    """
    logger.info(ASCII_LOGO)
    logger.info("Started deployment on SageMaker ...\n")

    try:
        endpoint_name = api_cloud.deploy(
            dir=_config().sagify_module_dir,
            s3_model_location=s3_model_location,
            num_instances=num_instances,
            ec2_type=ec2_type,
            docker_tag=obj['docker_tag'],
            aws_role=iam_role_arn,
            external_id=external_id,
            tags=aws_tags
        )

        logger.info("Model deployed to SageMaker successfully")
        logger.info("Endpoint name: {}".format(endpoint_name))
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command()
@click.option(
    u"-m", u"--s3-model-location",
    required=True,
    help="s3 location to model tar.gz",
    type=click.Path()
)
@click.option(
    u"-i", u"--s3-input-location",
    required=True,
    help="s3 input data location",
    type=click.Path()
)
@click.option(
    u"-o", u"--s3-output-location",
    required=True,
    help="s3 location to save predictions",
    type=click.Path()
)
@click.option(u"-n", u"--num-instances", required=True, type=int, help="Number of ec2 instances")
@click.option(u"-e", u"--ec2-type", required=True, help="ec2 instance type")
@click.option(
    u"-a", u"--aws-tags",
    callback=validate_tags,
    required=False,
    default=None,
    help='Tags for labeling a training job of the form "tag1=value1;tag2=value2". For more, see '
         'https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.'
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for the push command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
@click.pass_obj
def batch_transform(
        obj,
        s3_model_location,
        s3_input_location,
        s3_output_location,
        num_instances,
        ec2_type,
        aws_tags,
        iam_role_arn,
        external_id
):
    """
    Command to execute a batch transform job given a trained ML model on SageMaker
    """
    logger.info(ASCII_LOGO)
    logger.info("Started configuration of batch transform on SageMaker ...\n")

    try:
        api_cloud.batch_transform(
            dir=_config().sagify_module_dir,
            s3_model_location=s3_model_location,
            s3_input_location=s3_input_location,
            s3_output_location=s3_output_location,
            num_instances=num_instances,
            ec2_type=ec2_type,
            docker_tag=obj['docker_tag'],
            aws_role=iam_role_arn,
            external_id=external_id,
            tags=aws_tags
        )

        logger.info("Started batch transform on SageMaker successfully")
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


cloud.add_command(upload_data)
cloud.add_command(train)
cloud.add_command(hyperparameter_optimization)
cloud.add_command(deploy)
cloud.add_command(batch_transform)
