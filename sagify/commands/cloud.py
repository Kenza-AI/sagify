# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
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
    help="The AWS role to use for the train command"
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
    u"--use-spot-instances",
    default=False,
    is_flag=True,
    help="Optional flag that specifies whether to use SageMaker Managed Spot instances for training. "
         "It should be used only for training jobs that take less than 1 hour."
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
        use_spot_instances,
        metric_names
):
    """
    Command to train ML model(s) on SageMaker
    """
    logger.info(ASCII_LOGO)
    logger.info("Started training on SageMaker...\n")

    # Because MaxWaitTimeInSeconds is 3600 and cannot be less than training time out
    if use_spot_instances:
        time_out = 3600

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
            use_spot_instances=use_spot_instances,
            metric_names=[_val.strip() for _val in metric_names.split(',')] if metric_names else None
        )

        logger.info("Training on SageMaker succeeded")
        logger.info("Model S3 location: {}".format(s3_model_location))
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command(name='hyperparameter-optimization')
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
    help="The AWS role to use for the hyperparam command"
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
    u"--use-spot-instances",
    default=False,
    is_flag=True,
    help="Optional flag that specifies whether to use SageMaker Managed Spot instances for training. "
         "It should be used only for training jobs that take less than 1 hour."
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
        use_spot_instances,
        wait
):
    """
    Command for hyperparameter optimization on SageMaker
    """
    logger.info(ASCII_LOGO)
    logger.info("Started hyperparameter optimization on SageMaker...\n")

    # Because MaxWaitTimeInSeconds is 3600 and cannot be less than training time out
    if use_spot_instances:
        time_out = 3600

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
            use_spot_instances=use_spot_instances,
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
    help="The AWS role to use for the deploy command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
@click.option(
    u"--endpoint-name",
    required=False,
    default=None,
    help="Optional name for the SageMaker endpoint"
)
@click.pass_obj
def deploy(
        obj,
        s3_model_location,
        num_instances,
        ec2_type,
        aws_tags,
        iam_role_arn,
        external_id,
        endpoint_name
):
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
            tags=aws_tags,
            endpoint_name=endpoint_name
        )

        logger.info("Model deployed to SageMaker successfully")
        logger.info("Endpoint name: {}".format(endpoint_name))
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command(name="create-streaming-inference")
@click.option(
    u"-n",
    u"--name",
    required=True,
    help="Name of streaming inference worker"
)
@click.option(
    u"--endpoint-name",
    required=True,
    help="Name for the SageMaker endpoint"
)
@click.option(
    u"--input-topic-name",
    required=True,
    help="Name of input topic name"
)
@click.option(
    u"--output-topic-name",
    required=True,
    help="Name of output topic name"
)
@click.option(
    u"--type",
    required=False,
    default='SQS',
    help="Type of streaming inference pipeline. Only 'SQS' is supported right now."
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for this command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
def create_streaming_inference(
        name,
        endpoint_name,
        input_topic_name,
        output_topic_name,
        type,
        iam_role_arn,
        external_id
):
    """
    Command to set up a streaming inference pipeline
    """
    logger.info(ASCII_LOGO)
    logger.info("Experimental Functionality!\n")
    logger.info("Started creating streaming inference pipeline ...\n")

    try:
        config_file_path = os.path.join('.sagify.json')
        if not os.path.isfile(config_file_path):
            raise ValueError()

        config = ConfigManager(config_file_path).get_config()
        api_cloud.create_streaming_inference(
            dir=config.sagify_module_dir,
            name=name,
            endpoint_name=endpoint_name,
            input_topic_name=input_topic_name,
            output_topic_name=output_topic_name,
            type=type,
            aws_role=iam_role_arn,
            external_id=external_id
        )

        logger.info("Streaming inference pipeline has been created!")
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except Exception as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command(name="delete-streaming-inference")
@click.option(
    u"-n",
    u"--name",
    required=True,
    help="Name of streaming inference worker"
)
@click.option(
    u"--input-topic-name",
    required=True,
    help="Name of input topic name"
)
@click.option(
    u"--output-topic-name",
    required=True,
    help="Name of output topic name"
)
@click.option(
    u"--type",
    required=False,
    default='SQS',
    help="Type of streaming inference pipeline. Only 'SQS' is supported right now."
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for this command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
def delete_streaming_inference(
        name,
        input_topic_name,
        output_topic_name,
        type,
        iam_role_arn,
        external_id
):
    """
    Command to delete a streaming inference pipeline
    """
    logger.info(ASCII_LOGO)
    logger.info("Experimental Functionality!\n")
    logger.info("Started deleting streaming inference pipeline ...\n")

    try:
        config_file_path = os.path.join('.sagify.json')
        if not os.path.isfile(config_file_path):
            raise ValueError()

        config = ConfigManager(config_file_path).get_config()
        api_cloud.delete_streaming_inference(
            dir=config.sagify_module_dir,
            name=name,
            input_topic_name=input_topic_name,
            output_topic_name=output_topic_name,
            type=type,
            aws_role=iam_role_arn,
            external_id=external_id
        )

        logger.info("Streaming inference pipeline has been deleted!")
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except Exception as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command(name="send-to-streaming-inference")
@click.option(
    u"--input-features-file",
    required=True,
    help="Local path to input features file. Each line in the file is a json object.",
    type=click.Path(resolve_path=True)
)
@click.option(
    u"--input-topic-name",
    required=True,
    help="Name of input topic name"
)
@click.option(
    u"--type",
    required=False,
    default='SQS',
    help="Type of streaming inference pipeline. Only 'SQS' is supported right now."
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for this command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
def send_to_streaming_inference(
        input_features_file,
        input_topic_name,
        type,
        iam_role_arn,
        external_id
):
    """
    Send features to a streaming inference pipeline
    """
    logger.info(ASCII_LOGO)
    logger.info("Experimental Functionality!\n")
    logger.info("Started sending features to streaming inference pipeline ...\n")

    try:
        config_file_path = os.path.join('.sagify.json')
        if not os.path.isfile(config_file_path):
            raise ValueError()

        config = ConfigManager(config_file_path).get_config()
        api_cloud.send_to_streaming_inference(
            dir=config.sagify_module_dir,
            input_features_file=input_features_file,
            input_topic_name=input_topic_name,
            type=type,
            aws_role=iam_role_arn,
            external_id=external_id
        )

        logger.info("Features have been sent!")
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except Exception as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command(name="listen-to-streaming-inference")
@click.option(
    u"--output-topic-name",
    required=True,
    help="Name of output topic name"
)
@click.option(
    u"--type",
    required=False,
    default='SQS',
    help="Type of streaming inference pipeline. Only 'SQS' is supported right now."
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for this command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
def listen_to_streaming_inference(
        output_topic_name,
        type,
        iam_role_arn,
        external_id
):
    """
    Listen to predictions in a streaming inference pipeline
    """
    logger.info(ASCII_LOGO)
    logger.info("Experimental Functionality!\n")
    logger.info("Started listening to predictions in this streaming inference pipeline ...\n")

    try:
        config_file_path = os.path.join('.sagify.json')
        if not os.path.isfile(config_file_path):
            raise ValueError()

        config = ConfigManager(config_file_path).get_config()
        for _prediction in api_cloud.listen_to_streaming_inference(
            dir=config.sagify_module_dir,
            output_topic_name=output_topic_name,
            type=type,
            aws_role=iam_role_arn,
            external_id=external_id
        ):
            logger.info(_prediction)
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except Exception as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command(name="batch-transform")
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
    help="The AWS role to use for this command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
@click.option(
    u"-w",
    u"--wait",
    default=False,
    is_flag=True,
    help="Wait until Batch Transform is finished. "
         "Default: don't wait"
)
@click.option(
    u"--job-name",
    required=False,
    default=None,
    help="Optional name for the SageMaker batch transform job."
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
        external_id,
        wait,
        job_name
):
    """
    Command to execute a batch transform job given a trained ML model on SageMaker
    """
    logger.info(ASCII_LOGO)
    logger.info("Started configuration of batch transform on SageMaker ...\n")

    try:
        status = api_cloud.batch_transform(
            dir=_config().sagify_module_dir,
            s3_model_location=s3_model_location,
            s3_input_location=s3_input_location,
            s3_output_location=s3_output_location,
            num_instances=num_instances,
            ec2_type=ec2_type,
            docker_tag=obj['docker_tag'],
            aws_role=iam_role_arn,
            external_id=external_id,
            tags=aws_tags,
            wait=wait,
            job_name=job_name
        )

        if wait:
            logger.info("Batch transform on SageMaker finished with status: {}".format(status))
            if status == "Failed":
                sys.exit(1)
        else:
            logger.info("Started batch transform on SageMaker successfully")

    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


@click.command(name="lightning-deploy")
@click.option(
    u"--framework",
    required=True,
    help="Name of the ML framework. Valid values: sklearn, huggingface, xgboost"
)
@click.option(
    u"-m", u"--s3-model-location",
    required=False,
    help="s3 location to model tar.gz",
    type=click.Path()
)
@click.option(u"-n", u"--num-instances", required=True, type=int, help="Number of ec2 instances")
@click.option(u"-e", u"--ec2-type", required=True, help="ec2 instance type")
@click.option(
    u"--model-server-workers",
    required=False,
    type=int,
    default=None,
    help="The number of worker processes used by the inference server. "
         "If None, server will use one worker per vCPU")
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
    required=False,
    help="The AWS profile to use for the lightning deploy command"
)
@click.option(
    u"--aws-region",
    required=True,
    help="The AWS region to use for the lightning deploy command"
)
@click.option(
    u"-r",
    u"--iam-role-arn",
    required=False,
    help="The AWS role to use for the lightning deploy command"
)
@click.option(
    u"-x",
    u"--external-id",
    required=False,
    help="Optional external id used when using an IAM role"
)
@click.option(
    u"--endpoint-name",
    required=False,
    default=None,
    help="Name for the SageMaker endpoint"
)
@click.option(
    u"--extra-config-file",
    required=True,
    help="Json file with ML framework specific arguments",
    type=click.Path(resolve_path=True)
)
def lightning_deploy(
        framework,
        s3_model_location,
        num_instances,
        ec2_type,
        model_server_workers,
        aws_tags,
        aws_profile,
        aws_region,
        iam_role_arn,
        external_id,
        endpoint_name,
        extra_config_file
):
    """
    Command for lightning deployment of ML model(s) on SageMaker without code
    """
    logger.info(ASCII_LOGO)
    logger.info("Started lightning deployment on SageMaker ...\n")

    try:
        endpoint_name = api_cloud.lightning_deploy(
            framework=framework,
            s3_model_location=s3_model_location,
            num_instances=num_instances,
            ec2_type=ec2_type,
            aws_region=aws_region,
            model_server_workers=model_server_workers,
            aws_profile=aws_profile,
            aws_role=iam_role_arn,
            external_id=external_id,
            tags=aws_tags,
            endpoint_name=endpoint_name,
            extra_config_file=extra_config_file
        )

        logger.info("Model deployed to SageMaker successfully")
        logger.info("Endpoint name: {}".format(endpoint_name))
    except ValueError as e:
        logger.info("{}".format(e))
        sys.exit(-1)


cloud.add_command(upload_data)
cloud.add_command(train)
cloud.add_command(hyperparameter_optimization)
cloud.add_command(deploy)
cloud.add_command(create_streaming_inference)
cloud.add_command(delete_streaming_inference)
cloud.add_command(send_to_streaming_inference)
cloud.add_command(listen_to_streaming_inference)
cloud.add_command(batch_transform)
cloud.add_command(lightning_deploy)
