# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import json
import os

from sagemaker.parameter import CategoricalParameter, ContinuousParameter, IntegerParameter

from sagify.config.config import ConfigManager
from sagify.sagemaker import sagemaker
from sagify.streaming_inference.streaming_inference import StreamingInferenceClient


def _read_config(input_dir):
    config_file_path = os.path.join('.sagify.json')
    if not os.path.isfile(config_file_path):
        raise ValueError("This is not a sagify directory: {}".format(input_dir))

    return ConfigManager(config_file_path).get_config()


def _read_hyperparams_config(hyperparams_file_path):
    if not os.path.isfile(hyperparams_file_path):
        raise ValueError(
            "The given hyperparams file {} doens't exist".format(hyperparams_file_path)
        )

    with open(hyperparams_file_path) as _in_file:
        return json.load(_in_file)


def _read_hyperparams_ranges_config(hyperparams_config_file_path):
    if not os.path.isfile(hyperparams_config_file_path):
        raise ValueError(
            "The given hyperparams file {} doesn't exist".format(hyperparams_config_file_path)
        )

    with open(hyperparams_config_file_path) as _in_file:
        hyperparams_config_dict = json.load(_in_file)

    if 'ParameterRanges' not in hyperparams_config_dict:
        raise ValueError("ParameterRanges not in the hyperparams file")

    parameter_ranges_dict = hyperparams_config_dict['ParameterRanges']

    if not parameter_ranges_dict:
        raise ValueError("Empty ParameterRanges in the hyperparams file")

    if 'ObjectiveMetric' not in hyperparams_config_dict and 'Name' not in hyperparams_config_dict['ObjectiveMetric']:
        raise ValueError("ObjectiveMetric not in the hyperparams file")

    objective_name = hyperparams_config_dict['ObjectiveMetric']['Name']
    objective_type = hyperparams_config_dict['ObjectiveMetric']['Type']

    hyperparameter_ranges = {}

    categorical_param_ranges_dict = parameter_ranges_dict['CategoricalParameterRanges']
    for _dict in categorical_param_ranges_dict:
        hyperparameter_ranges[_dict['Name']] = CategoricalParameter(_dict['Values'])

    integer_param_ranges_dict = parameter_ranges_dict['IntegerParameterRanges']
    for _dict in integer_param_ranges_dict:
        hyperparameter_ranges[_dict['Name']] = IntegerParameter(_dict['MinValue'], _dict['MaxValue'])

    continuous_param_ranges_dict = parameter_ranges_dict['ContinuousParameterRanges']
    for _dict in continuous_param_ranges_dict:
        hyperparameter_ranges[_dict['Name']] = ContinuousParameter(_dict['MinValue'], _dict['MaxValue'])

    return objective_name, objective_type, hyperparameter_ranges


def upload_data(dir, input_dir, s3_dir):
    """
    Uploads data to S3

    :param dir: [str], source root directory
    :param input_dir: [str], path to local data input directory
    :param s3_dir: [str], S3 location to upload data

    :return: [str], S3 location to upload data
    """
    config = _read_config(dir)
    sage_maker_client = sagemaker.SageMakerClient(config.aws_profile, config.aws_region)

    return sage_maker_client.upload_data(input_dir, s3_dir)


def train(
        dir,
        input_s3_dir,
        output_s3_dir,
        hyperparams_file,
        ec2_type,
        volume_size,
        time_out,
        docker_tag,
        aws_role,
        external_id,
        base_job_name,
        job_name,
        use_spot_instances=False,
        metric_names=None,
        tags=None
):
    """
    Trains ML model(s) on SageMaker

    :param dir: [str], source root directory
    :param input_s3_dir: [str], S3 location to input data
    :param output_s3_dir: [str], S3 location to save output (models, etc)
    :param hyperparams_file: [str], path to hyperparams json file
    :param ec2_type: [str], ec2 instance type. Refer to:
    https://aws.amazon.com/sagemaker/pricing/instance-types/
    :param volume_size: [int], size in GB of the EBS volume
    :param time_out: [int], time-out in seconds
    :param docker_tag: [str], the Docker tag for the image
    :param aws_role: [str], the AWS role assumed by SageMaker while training
    :param external_id: [str], Optional external id used when using an IAM role
    :param base_job_name: [str], Optional prefix for the SageMaker training job
    :param job_name: [str], Optional name for the SageMaker training job. Overrides `base_job_name`
    :param use_spot_instances: bool, default=False], Specifies whether to use SageMaker
                Managed Spot instances for training.

                More information:
                https://docs.aws.amazon.com/sagemaker/latest/dg/model-managed-spot-training.html
                (default: ``False``).
    :param metric_names: [list[str], default=None], Optional list of string metric names
    :param tags: [optional[list[dict]], default: None], List of tags for labeling a training
        job. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html. Example:

        [
            {
                'Key': 'key_name_1',
                'Value': key_value_1,
            },
            {
                'Key': 'key_name_2',
                'Value': key_value_2,
            },
            ...
        ]
    :return: [str], S3 model location
    """
    config = _read_config(dir)
    hyperparams_dict = _read_hyperparams_config(hyperparams_file) if hyperparams_file else None
    sage_maker_client = sagemaker.SageMakerClient(config.aws_profile, config.aws_region, aws_role, external_id)

    image_name = config.image_name+':'+docker_tag

    return sage_maker_client.train(
        image_name=image_name,
        input_s3_data_location=input_s3_dir,
        train_instance_count=1,
        train_instance_type=ec2_type,
        train_volume_size=volume_size,
        train_max_run=time_out,
        output_path=output_s3_dir,
        hyperparameters=hyperparams_dict,
        base_job_name=base_job_name,
        job_name=job_name,
        use_spot_instances=use_spot_instances,
        tags=tags,
        metric_names=metric_names
    )


def hyperparameter_optimization(
        dir,
        input_s3_dir,
        output_s3_dir,
        hyperparams_config_file,
        ec2_type,
        max_jobs,
        max_parallel_jobs,
        volume_size,
        time_out,
        docker_tag,
        aws_role,
        external_id,
        base_job_name,
        job_name,
        wait,
        use_spot_instances=False,
        tags=None
):
    """
    Hyperparameter Optimization on SageMaker

    :param dir: [str], source root directory
    :param input_s3_dir: [str], S3 location to input data
    :param output_s3_dir: [str], S3 location to save the multiple trained models
    :param hyperparams_config_file: [str], path to hyperparameters config json file
    :param ec2_type: [str], ec2 instance type. Refer to:
    https://aws.amazon.com/sagemaker/pricing/instance-types/
    :param max_jobs: [int], Maximum total number of training jobs to start for the hyperparameter tuning job
    :param max_parallel_jobs: [int], Maximum number of parallel training jobs to start
    :param volume_size: [int], size in GB of the EBS volume
    :param time_out: [int], time-out in seconds
    :param docker_tag: [str], the Docker tag for the image
    :param aws_role: [str], the AWS role assumed by SageMaker while training
    :param external_id: [str], Optional external id used when using an IAM role
    :param base_job_name: [str], Optional prefix for the SageMaker training job
    :param job_name: [str], Optional name for the SageMaker tuning job. Overrides `base_job_name`
    :param wait: [bool, default=False], Wait until hyperparameter tuning is done
    :param use_spot_instances: bool, default=False], Specifies whether to use SageMaker
                Managed Spot instances for training.

                More information:
                https://docs.aws.amazon.com/sagemaker/latest/dg/model-managed-spot-training.html
                (default: ``False``).
    :param tags: [optional[list[dict]], default: None], List of tags for labeling a training
        job. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html. Example:

        [
            {
                'Key': 'key_name_1',
                'Value': key_value_1,
            },
            {
                'Key': 'key_name_2',
                'Value': key_value_2,
            },
            ...
        ]
    :return: [str], S3 model location
    """
    config = _read_config(dir)
    objective_metric_name, objective_type, hyperparams_ranges_dict = _read_hyperparams_ranges_config(
        hyperparams_config_file
    )
    sage_maker_client = sagemaker.SageMakerClient(config.aws_profile, config.aws_region, aws_role, external_id)

    image_name = config.image_name+':'+docker_tag

    return sage_maker_client.hyperparameter_optimization(
        image_name=image_name,
        input_s3_data_location=input_s3_dir,
        instance_count=1,
        instance_type=ec2_type,
        volume_size=volume_size,
        objective_type=objective_type,
        objective_metric_name=objective_metric_name,
        max_jobs=max_jobs,
        max_parallel_jobs=max_parallel_jobs,
        max_run=time_out,
        output_path=output_s3_dir,
        hyperparams_ranges_dict=hyperparams_ranges_dict,
        base_job_name=base_job_name,
        job_name=job_name,
        use_spot_instances=use_spot_instances,
        tags=tags,
        wait=wait
    )


def deploy(
        dir,
        s3_model_location,
        num_instances,
        ec2_type,
        docker_tag,
        aws_role=None,
        external_id=None,
        tags=None,
        endpoint_name=None
):
    """
    Deploys ML model(s) on SageMaker

    :param dir: [str], source root directory
    :param s3_model_location: [str], S3 model location
    :param num_instances: [int], number of ec2 instances
    :param ec2_type: [str], ec2 instance type. Refer to:
    https://aws.amazon.com/sagemaker/pricing/instance-types/
    :param docker_tag: [str], the Docker tag for the image
    :param aws_role: [str], the AWS role assumed by SageMaker while deploying
    :param external_id: [str], Optional external id used when using an IAM role
    :param tags: [optional[list[dict]], default: None], List of tags for labeling a training
        job. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html. Example:

        [
            {
                'Key': 'key_name_1',
                'Value': key_value_1,
            },
            {
                'Key': 'key_name_2',
                'Value': key_value_2,
            },
            ...
        ]
    :param endpoint_name: [optional[str]], Optional name for the SageMaker endpoint

    :return: [str], endpoint name
    """
    config = _read_config(dir)
    image_name = config.image_name+':'+docker_tag

    sage_maker_client = sagemaker.SageMakerClient(config.aws_profile, config.aws_region, aws_role, external_id)
    return sage_maker_client.deploy(
        image_name=image_name,
        s3_model_location=s3_model_location,
        train_instance_count=num_instances,
        train_instance_type=ec2_type,
        tags=tags,
        endpoint_name=endpoint_name
    )


def create_streaming_inference(
        dir,
        name,
        endpoint_name,
        input_topic_name,
        output_topic_name,
        type='SQS',
        aws_role=None,
        external_id=None
):
    """
    Set up a streaming inference pipeline

    :param dir: [str], Source root directory
    :param name: [str], Name of streaming inference worker
    :param endpoint_name: [str], Name of the SageMaker endpoint
    :param input_topic_name: [str], Name of input topic name
    :param output_topic_name: [str], Name of output topic name
    :param type: [str, default='SQS'], Type of streaming inference pipeline. Only SQS is supported right now.
    :param aws_role: [str], the AWS role assumed by SageMaker while deploying
    :param external_id: [str], Optional external id used when using an IAM role

    """
    zipped_lambda_handler_path = os.path.relpath(os.path.join(dir, 'sagify_base', 'lambda', 'lambda_handler.zip'))

    config = _read_config(dir)
    streaming_inference_client = StreamingInferenceClient(
        aws_profile=config.aws_profile,
        aws_region=config.aws_region,
        aws_role=aws_role,
        external_id=external_id
    )

    streaming_inference_client.create_inference_pipeline(
        name=name,
        path_to_zipped_code=zipped_lambda_handler_path,
        input_topic_name=input_topic_name,
        output_topic_name=output_topic_name,
        endpoint_name=endpoint_name,
        type=type
    )


def delete_streaming_inference(
        dir,
        name,
        input_topic_name,
        output_topic_name,
        type='SQS',
        aws_role=None,
        external_id=None
):
    """
    Delete a streaming inference pipeline

    :param dir: [str], Source root directory
    :param name: [str], Name of streaming inference worker
    :param input_topic_name: [str], Name of input topic name
    :param output_topic_name: [str], Name of output topic name
    :param type: [str, default='SQS'], Type of streaming inference pipeline. Only SQS is supported right now.
    :param aws_role: [str], the AWS role assumed by SageMaker while deploying
    :param external_id: [str], Optional external id used when using an IAM role

    """
    config = _read_config(dir)
    streaming_inference_client = StreamingInferenceClient(
        aws_profile=config.aws_profile,
        aws_region=config.aws_region,
        aws_role=aws_role,
        external_id=external_id
    )

    streaming_inference_client.delete_inference_pipeline(
        name=name,
        input_topic_name=input_topic_name,
        output_topic_name=output_topic_name,
        type=type
    )


def send_to_streaming_inference(
        dir,
        input_features_file,
        input_topic_name,
        type='SQS',
        aws_role=None,
        external_id=None
):
    """
    Send features to a streaming inference pipeline

    :param dir: [str], Source root directory
    :param input_features_file: [str], Local path to input features file. Each line in the file is a json object.
    :param input_topic_name: [str], Name of input topic name
    :param type: [str, default='SQS'], Type of streaming inference pipeline. Only SQS is supported right now.
    :param aws_role: [str], the AWS role assumed by SageMaker while deploying
    :param external_id: [str], Optional external id used when using an IAM role

    """
    config = _read_config(dir)
    streaming_inference_client = StreamingInferenceClient(
        aws_profile=config.aws_profile,
        aws_region=config.aws_region,
        aws_role=aws_role,
        external_id=external_id
    )

    streaming_inference_client.send_to_streaming_inference(
        input_features_file=input_features_file,
        input_topic_name=input_topic_name,
        type=type
    )


def listen_to_streaming_inference(
        dir,
        output_topic_name,
        type='SQS',
        aws_role=None,
        external_id=None
):
    """
    Listen to predictions in a streaming inference pipeline

    :param dir: [str], Source root directory
    :param output_topic_name: [str], Name of output topic name
    :param type: [str, default='SQS'], Type of streaming inference pipeline. Only SQS is supported right now.
    :param aws_role: [str], the AWS role assumed by SageMaker while deploying
    :param external_id: [str], Optional external id used when using an IAM role

    """
    config = _read_config(dir)
    streaming_inference_client = StreamingInferenceClient(
        aws_profile=config.aws_profile,
        aws_region=config.aws_region,
        aws_role=aws_role,
        external_id=external_id
    )

    return streaming_inference_client.listen_to_streaming_inference(
        output_topic_name=output_topic_name,
        type=type
    )


def batch_transform(
        dir,
        s3_model_location,
        s3_input_location,
        s3_output_location,
        num_instances,
        ec2_type,
        docker_tag,
        aws_role=None,
        external_id=None,
        tags=None,
        wait=False,
        job_name=None
):
    """
    Executes a batch transform job given a trained ML model on SageMaker

    :param dir: [str], source root directory
    :param s3_model_location: [str], S3 model location
    :param s3_input_location: [str], S3 input data location
    :param s3_output_location: [str], S3 location to save predictions
    :param num_instances: [int], number of ec2 instances
    :param ec2_type: [str], ec2 instance type. Refer to:
    https://aws.amazon.com/sagemaker/pricing/instance-types/
    :param docker_tag: [str], the Docker tag for the image
    :param aws_role: [str], the AWS role assumed by SageMaker while deploying
    :param external_id: [str], Optional external id used when using an IAM role
    :param tags: [optional[list[dict]], default: None], List of tags for labeling a training
        job. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html. Example:

        [
            {
                'Key': 'key_name_1',
                'Value': key_value_1,
            },
            {
                'Key': 'key_name_2',
                'Value': key_value_2,
            },
            ...
        ]
    :param wait: [bool, default=False], wait or not for the batch transform to finish
    :param job_name: [str, default=None], name for the SageMaker batch transform job

    :return: [str], transform job status if wait=True.
    Valid values: 'InProgress'|'Completed'|'Failed'|'Stopping'|'Stopped'
    """
    config = _read_config(dir)
    image_name = config.image_name + ':' + docker_tag

    sage_maker_client = sagemaker.SageMakerClient(config.aws_profile, config.aws_region, aws_role, external_id)
    return sage_maker_client.batch_transform(
        image_name=image_name,
        s3_model_location=s3_model_location,
        s3_input_location=s3_input_location,
        s3_output_location=s3_output_location,
        transform_instance_count=num_instances,
        transform_instance_type=ec2_type,
        tags=tags,
        wait=wait,
        job_name=job_name
    )


def lightning_deploy(
        framework,
        num_instances,
        ec2_type,
        aws_region,
        s3_model_location=None,
        model_server_workers=None,
        aws_profile=None,
        aws_role=None,
        external_id=None,
        tags=None,
        endpoint_name=None,
        extra_config_file=None
):
    """
    Deploys ML model(s) on SageMaker without code

    :param framework: [str], The name of the ML framework. Valid values: sklearn, huggingface
    :param num_instances: [int], number of ec2 instances
    :param ec2_type: [str], ec2 instance type. Refer to:
    https://aws.amazon.com/sagemaker/pricing/instance-types/
    :param aws_region: [str], the AWS region
    :param s3_model_location: [str], S3 model location
    :param model_server_workers: [int], Optional number of worker processes used by the inference
    server. If None, server will use one worker per vCPU.
    :param aws_profile: [optional[str]], Optional AWS profile
    :param aws_role: [optional[str]], Optional AWS role assumed by SageMaker while deploying
    :param external_id: [optional[str]], Optional external id used when using an IAM role
    :param tags: [optional[list[dict]], default: None], List of tags for labeling a training
        job. For more, see https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html. Example:

        [
            {
                'Key': 'key_name_1',
                'Value': key_value_1,
            },
            {
                'Key': 'key_name_2',
                'Value': key_value_2,
            },
            ...
        ]
    :param endpoint_name: [optional[str]], Optional name for the SageMaker endpoint
    :param extra_config_file: [optional[str]], Optional Json file with ML framework specific arguments

    :return: [str], endpoint name
    """
    sage_maker_client = sagemaker.SageMakerClient(aws_profile, aws_region, aws_role, external_id)

    if not os.path.isfile(extra_config_file):
        raise ValueError(
            "The given extra config file {} doesn't exist".format(extra_config_file)
        )

    with open(extra_config_file) as _in_file:
        extra_config_dict = json.load(_in_file)

    if framework == 'sklearn':
        return sage_maker_client.deploy_sklearn(
            s3_model_location=s3_model_location,
            instance_count=num_instances,
            instance_type=ec2_type,
            model_server_workers=model_server_workers,
            tags=tags,
            endpoint_name=endpoint_name,
            **extra_config_dict
        )
    elif framework == 'huggingface':
        return sage_maker_client.deploy_hugging_face(
            s3_model_location=s3_model_location,
            instance_count=num_instances,
            instance_type=ec2_type,
            model_server_workers=model_server_workers,
            tags=tags,
            endpoint_name=endpoint_name,
            **extra_config_dict
        )

    raise ValueError("Invalid framework value")
