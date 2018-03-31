import os

from six.moves.urllib.parse import urlparse

import boto3
import sagemaker


class SageMakerClient(object):
    def __init__(self, aws_profile, aws_region):
        self.boto_session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        self.sagemaker_session = sagemaker.Session(boto_session=self.boto_session)

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
            hyperparameters
    ):
        role = sagemaker.get_execution_role(self.sagemaker_session)
        account = self.boto_session.client('sts').get_caller_identity()['Account']
        region = self.boto_session.region_name
        image = '{account}.dkr.ecr.{region}.amazonaws.com/{image}:latest'.format(
            account=account,
            region=region,
            image=image_name
        )

        estimator = sagemaker.estimator.Estimator(
            image_name=image,
            role=role,
            train_instance_count=train_instance_count,
            train_instance_type=train_instance_type,
            train_volume_size=train_volume_size,
            train_max_run=train_max_run,
            input_mode='File',
            output_path=output_path,
            hyperparameters=hyperparameters,
            sagemaker_session=self.sagemaker_session
        )

        estimator.fit(input_s3_data_location)

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
