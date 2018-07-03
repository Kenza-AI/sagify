from __future__ import absolute_import

import os

import sagemaker as sage
from six.moves.urllib.parse import urlparse

import boto3


class SageMakerClient(object):
    def __init__(self, aws_profile, aws_region):
        self.boto_session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        self.sagemaker_session = sage.Session(boto_session=self.boto_session)
        self.role = sage.get_execution_role(self.sagemaker_session)

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
        image = self._construct_image_location(image_name)

        estimator = sage.estimator.Estimator(
            image_name=image,
            role=self.role,
            train_instance_count=train_instance_count,
            train_instance_type=train_instance_type,
            train_volume_size=train_volume_size,
            train_max_run=train_max_run,
            input_mode='File',
            output_path=output_path,
            hyperparameters=hyperparameters,
            sagemaker_session=self.sagemaker_session
        )
        if tags:
            estimator.tags = tags

        estimator.fit(input_s3_data_location)

        return estimator.model_data

    def deploy(
            self,
            image_name,
            s3_model_location,
            train_instance_count,
            train_instance_type,
            tags=None
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
        :return: [str], endpoint name
        """
        image = self._construct_image_location(image_name)

        model = sage.Model(
            model_data=s3_model_location,
            image=image,
            role=self.role,
            sagemaker_session=self.sagemaker_session
        )

        model.deploy(
            initial_instance_count=train_instance_count,
            instance_type=train_instance_type,
            tags=tags
        )

        return model.endpoint_name

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

        return '{account}.dkr.ecr.{region}.amazonaws.com/{image}:latest'.format(
            account=account,
            region=region,
            image=image_name
        )
