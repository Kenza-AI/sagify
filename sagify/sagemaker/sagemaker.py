# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

import sagemaker as sage
import sagemaker.tuner
import sagemaker.huggingface
import sagemaker.sklearn.model
from six.moves.urllib.parse import urlparse

import boto3
import botocore

from sagify.log import logger


_FILE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
_METRIC_REGEX = "([0-9\\.]+)"


class SageMakerClient(object):
    def __init__(self, aws_profile, aws_region, aws_role=None, external_id=None):

        if aws_role:
            logger.info("An IAM role and corresponding external id were provided. Attempting to assume that role...")

            sts_client = boto3.client('sts')
            if external_id is None:
                assumedRoleObject = sts_client.assume_role(
                    RoleArn=aws_role,
                    RoleSessionName="SagifySession"
                )
            else:
                assumedRoleObject = sts_client.assume_role(
                    RoleArn=aws_role,
                    RoleSessionName="SagifySession",
                    ExternalId=external_id
                )

            credentials = assumedRoleObject['Credentials']
            self.boto_session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=aws_region
            )
        elif aws_profile:
            logger.info("No IAM role provided. Using profile {} instead.".format(aws_profile))
            self.boto_session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        else:
            self.boto_session = boto3.Session(region_name=aws_region)

        self.sagemaker_client = self.boto_session.client('sagemaker')
        self.sagemaker_session = sage.Session(boto_session=self.boto_session)
        self.role = sage.get_execution_role(self.sagemaker_session) if aws_role is None else aws_role

    def upload_data(self, input_dir, s3_dir):
        """
        Uploads data to S3
        :param input_dir: [str], local input directory where files are located
        :param s3_dir: [str], S3 directory to upload files
        :return: [str], S3 path where data are uploaded
        """
        bucket = SageMakerClient._get_s3_bucket(s3_dir)
        prefix = SageMakerClient._get_s3_key_prefix(s3_dir) or 'data'
        self.sagemaker_session.upload_data(path=input_dir, bucket=bucket, key_prefix=prefix)

        return os.path.join('s3://', bucket, prefix)

    def train(
            self,
            image_name,
            input_s3_data_location,
            train_instance_count,
            train_instance_type,
            train_volume_size,
            train_max_run,
            output_path,
            hyperparameters,
            base_job_name,
            job_name,
            use_spot_instances=False,
            metric_names=None,
            tags=None
    ):
        """
        Train model on SageMaker
        :param image_name: [str], name of Docker image
        :param input_s3_data_location: [str], S3 location to input data
        :param train_instance_count: [str], number of ec2 instances
        :param train_instance_type: [str], ec2 instance type
        :param train_volume_size: [str], size in GB of the EBS volume to use for storing input data
        :param train_max_run: [str], Timeout in seconds for training
        :param output_path: [str], S3 location for saving the training
        result (model artifacts and output files)
        :param hyperparameters: [dict], Dictionary containing the hyperparameters to initialize
        this estimator with
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

        :return: [str], the model location in S3
        """
        if metric_names is None:
            metric_names = []
        image = self._construct_image_location(image_name)

        metric_definitions = [
            {'Name': _name, 'Regex': '{}: {}'.format(_name, _METRIC_REGEX)} for _name in metric_names
        ] if metric_names else None

        estimator = sage.estimator.Estimator(
            image_uri=image,
            role=self.role,
            instance_count=train_instance_count,
            instance_type=train_instance_type,
            volume_size=train_volume_size,
            max_run=train_max_run,
            input_mode='File',
            output_path=output_path,
            hyperparameters=hyperparameters,
            base_job_name=base_job_name,
            sagemaker_session=self.sagemaker_session,
            metric_definitions=metric_definitions,
            use_spot_instances=use_spot_instances,
            max_wait=3600 if use_spot_instances else None  # 1 hour
        )
        if tags:
            estimator.tags = tags

        estimator.fit(input_s3_data_location, job_name=job_name)

        return estimator.model_data

    def hyperparameter_optimization(
            self,
            image_name,
            input_s3_data_location,
            instance_count,
            instance_type,
            objective_type,
            objective_metric_name,
            max_jobs,
            max_parallel_jobs,
            volume_size,
            max_run,
            output_path,
            hyperparams_ranges_dict,
            base_job_name,
            job_name,
            use_spot_instances=False,
            tags=None,
            wait=False
    ):
        """
        Hyperparameter Optimization on SageMaker

        :param image_name: [str], name of Docker image
        :param input_s3_data_location: [str], S3 location to input data
        :param instance_count: [str], number of ec2 instances
        :param instance_type: [str], ec2 instance type
        :param objective_type: [str], The type of the objective metric for evaluating training jobs.
        This value can be either ‘Minimize’ or ‘Maximize’
        :param objective_metric_name: [str], Name of objective
        :param max_jobs: [int], Maximum total number of training jobs to start for the hyperparameter tuning job
        :param max_parallel_jobs: [int], Maximum number of parallel training jobs to start
        :param volume_size: [str], size in GB of the EBS volume to use for storing input data
        :param max_run: [str], Timeout in seconds for training
        :param output_path: [str], S3 location to save the multiple trained models
        :param hyperparams_ranges_dict: [dict], Dictionary containing the hyperparameters configuration
        :param base_job_name: [str], Optional prefix for the SageMaker tuning job.
        :param job_name: [str], Optional name for the SageMaker tuning job. Overrides `base_job_name`
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
        :param wait: [bool, default=False], Wait until hyperparameter tuning is done

        :return: [str], the model location in S3
        """
        image = self._construct_image_location(image_name)

        estimator = sage.estimator.Estimator(
            image_uri=image,
            role=self.role,
            instance_count=instance_count,
            instance_type=instance_type,
            volume_size=volume_size,
            max_run=max_run,
            input_mode='File',
            output_path=output_path,
            sagemaker_session=self.sagemaker_session,
            use_spot_instances=use_spot_instances,
            max_wait=3600 if use_spot_instances else None  # 1 hour
        )

        metric_definitions = [
            {
                'Name': objective_metric_name,
                'Regex': '{}: {}'.format(objective_metric_name, _METRIC_REGEX)
            }
        ]

        tuner = sagemaker.tuner.HyperparameterTuner(
            estimator=estimator,
            objective_metric_name=objective_metric_name,
            hyperparameter_ranges=hyperparams_ranges_dict,
            metric_definitions=metric_definitions,
            max_jobs=max_jobs,
            max_parallel_jobs=max_parallel_jobs,
            objective_type=objective_type,
            base_tuning_job_name=base_job_name
        )

        if tags:
            tuner.tags = tags

        tuner.fit(input_s3_data_location, job_name=job_name)

        if wait:
            tuner.wait()

            return tuner.best_training_job()

        return None

    def deploy(
            self,
            image_name,
            s3_model_location,
            train_instance_count,
            train_instance_type,
            tags=None,
            endpoint_name=None
    ):
        """
        Deploy model to SageMaker
        :param image_name: [str], name of Docker image
        :param s3_model_location: [str], model location in S3
        :param train_instance_count: [str],  number of ec2 instances
        :param train_instance_type: [str], ec2 instance type
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
        image = self._construct_image_location(image_name)

        model = sage.Model(
            model_data=s3_model_location,
            image_uri=image,
            role=self.role,
            sagemaker_session=self.sagemaker_session
        )

        try:
            model.deploy(
                initial_instance_count=train_instance_count,
                instance_type=train_instance_type,
                tags=tags,
                endpoint_name=endpoint_name
            )

            return model.endpoint_name
        except botocore.exceptions.ClientError:
            # ValueError raised if there is no endpoint already
            predictor = sage.Predictor(
                endpoint_name=endpoint_name,
                sagemaker_session=self.sagemaker_session
            )

            predictor.update_endpoint(
                initial_instance_count=train_instance_count,
                instance_type=train_instance_type,
                tags=tags,
                model_name=model.name
            )

            return predictor.endpoint_name

    def batch_transform(
            self,
            image_name,
            s3_model_location,
            s3_input_location,
            s3_output_location,
            transform_instance_count,
            transform_instance_type,
            tags=None,
            wait=False,
            job_name=None
    ):
        """
        Execute batch transform on a trained model to SageMaker
        :param image_name: [str], name of Docker image
        :param s3_model_location: [str], model location in S3
        :param s3_input_location: [str], S3 input data location
        :param s3_output_location: [str], S3 output data location
        :param transform_instance_count: [str],  number of ec2 instances
        :param transform_instance_type: [str], ec2 instance type
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
        image = self._construct_image_location(image_name)

        model = sage.Model(
            model_data=s3_model_location,
            image_uri=image,
            role=self.role,
            sagemaker_session=self.sagemaker_session
        )

        content_type = "application/json"

        transformer = model.transformer(
            instance_type=transform_instance_type,
            instance_count=transform_instance_count,
            assemble_with='Line',
            output_path=s3_output_location,
            tags=tags,
            accept=content_type,
            strategy="SingleRecord"
        )

        transformer.transform(data=s3_input_location, split_type='Line', content_type=content_type, job_name=job_name)

        if wait:
            try:
                transformer.wait()
            except Exception:
                # If there is an error, wait() throws an exception and we're not able to return a Failed status
                pass
            finally:
                job_name = transformer.latest_transform_job.job_name
                job_description = self.sagemaker_client.describe_transform_job(TransformJobName=job_name)

            return job_description['TransformJobStatus']

    def deploy_sklearn(
            self,
            s3_model_location,
            instance_count,
            instance_type,
            framework_version,
            model_server_workers=None,
            tags=None,
            endpoint_name=None
    ):
        model = sagemaker.sklearn.model.SKLearnModel(
            role=self.role,
            model_data=s3_model_location,
            framework_version=framework_version,
            py_version="py3",
            source_dir=os.path.join(_FILE_DIR_PATH, "sklearn_code"),
            entry_point="sklearn_inference.py",
            model_server_workers=model_server_workers,
            sagemaker_session=self.sagemaker_session
        )

        try:
            predictor = model.deploy(
                instance_type=instance_type,
                initial_instance_count=instance_count,
                tags=tags,
                endpoint_name=endpoint_name
            )
        except botocore.exceptions.ClientError:
            # ValueError raised if there is no endpoint already
            predictor = sage.Predictor(
                endpoint_name=endpoint_name,
                sagemaker_session=self.sagemaker_session
            )

            predictor.update_endpoint(
                initial_instance_count=instance_count,
                instance_type=instance_type,
                tags=tags,
                model_name=model.name
            )

        return predictor.endpoint_name

    def deploy_hugging_face(
            self,
            instance_count,
            instance_type,
            transformers_version=None,
            pytorch_version=None,
            tensorflow_version=None,
            s3_model_location=None,
            hub=None,
            model_server_workers=None,
            tags=None,
            endpoint_name=None
    ):
        def _validate_either_of_them(name_a, name_b, var_a, var_b):
            if var_a is not None and var_b is not None:
                raise ValueError(
                    f'{name_a} and {name_b} are both not None. '
                    f'Specify only {name_a} or {name_b}.'
                )
            if var_a is None and var_b is None:
                raise ValueError(
                    "{name_a} and {name_b} are both None. "
                    "Specify either {name_a} or {name_b}."
                )

        _validate_either_of_them(
            name_a='pytorch_version',
            name_b='tensorflow_version',
            var_a=pytorch_version,
            var_b=tensorflow_version
        )

        _validate_either_of_them(
            name_a='model_location',
            name_b='hub',
            var_a=s3_model_location,
            var_b=hub
        )

        model = sagemaker.huggingface.HuggingFaceModel(
            role=self.role,
            model_data=s3_model_location,
            transformers_version=transformers_version,
            pytorch_version=pytorch_version,
            tensorflow_version=tensorflow_version,
            model_server_workers=model_server_workers,
            py_version='py36',
            env=hub,
            sagemaker_session=self.sagemaker_session
        )

        try:
            predictor = model.deploy(
                instance_type=instance_type,
                initial_instance_count=instance_count,
                tags=tags,
                endpoint_name=endpoint_name
            )
        except botocore.exceptions.ClientError:
            # ValueError raised if there is no endpoint already
            predictor = sage.Predictor(
                endpoint_name=endpoint_name,
                sagemaker_session=self.sagemaker_session
            )

            predictor.update_endpoint(
                initial_instance_count=instance_count,
                instance_type=instance_type,
                tags=tags,
                model_name=model.name
            )

        return predictor.endpoint_name

    @staticmethod
    def _get_s3_bucket(s3_dir):
        """
        Extract bucket from S3 dir
        :param s3_dir: [str], input S3 directory
        :return: [str], extracted bucket name
        """
        return urlparse(s3_dir).netloc

    @staticmethod
    def _get_s3_key_prefix(s3_dir):
        """
        Extract key prefix from S3 dir
        :param s3_dir: [str], input S3 directory
        :return: [str], extracted key prefix name
        """
        return urlparse(s3_dir).path.lstrip('/').rstrip('/')

    def _construct_image_location(self, image_name):
        account = self.boto_session.client('sts').get_caller_identity()['Account']
        region = self.boto_session.region_name

        return '{account}.dkr.ecr.{region}.amazonaws.com/{image}'.format(
            account=account,
            region=region,
            image=image_name
        )
