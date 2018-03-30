import os

from six.moves.urllib.parse import urlparse

import boto3
import sagemaker


class SageMakerClient(object):
    def __init__(self, aws_profile, aws_region):
        self.boto_session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        self.session = sagemaker.Session(boto_session=self.boto_session)

    def upload_data(self, input_dir, s3_dir):
        """
        Uploads data to S3
        :param input_dir: [str], local input directory where files are located
        :param s3_dir: [str], S3 directory to upload files
        :return: [str], S3 path where data are uploaded
        """
        bucket = SageMakerClient._get_s3_bucket(s3_dir)
        prefix = SageMakerClient._get_s3_key_prefix(s3_dir) or 'data'
        self.session.upload_data(path=input_dir, bucket=bucket, key_prefix=prefix)

        return os.path.join('s3://', bucket, prefix)

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
