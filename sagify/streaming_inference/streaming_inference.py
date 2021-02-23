# -*- coding: utf-8 -*-
from __future__ import absolute_import

import boto3
import sagemaker as sage

from sagify.log import logger


class StreamingInferenceClient(object):
    def __init__(self, aws_profile, aws_region, aws_role=None, external_id=None):
        self.aws_region = aws_region

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

        self.lambda_client = self.boto_session.client('lambda')
        self.sqs_client = self.boto_session.client('sqs')

        self.sagemaker_session = sage.Session(boto_session=self.boto_session)
        self.role = sage.get_execution_role(self.sagemaker_session) if aws_role is None else aws_role

    def create_inference_pipeline(
            self,
            name,
            path_to_zipped_code,
            input_topic_name,
            output_topic_name,
            endpoint_name,
            type='SQS'
    ):
        """
        Create a streaming inference pipeline

        :param name: [str], Name of streaming inference
        :param path_to_zipped_code: [str], Path to lambda handler zipped code
        :param input_topic_name: [str], Name of input topic name
        :param output_topic_name: [str], Name of output topic name
        :param endpoint_name: [str], Name of the SageMaker endpoint
        :param type: [str, default='SQS'], Type of streaming inference pipeline. Only SQS is supported right now.
        """
        input_queue_url = self.sqs_client.create_queue(
            QueueName=input_topic_name,
            Attributes={
                'VisibilityTimeout': '900'
            }
        )['QueueUrl']

        self.sqs_client.create_queue(
            QueueName=output_topic_name,
            Attributes={
                'VisibilityTimeout': '900'
            }
        )

        with open(path_to_zipped_code, 'rb') as f:
            zipped_code = f.read()

        env_variables = {
            'REGION_NAME': self.aws_region,
            'SAGEMAKER_ENDPOINT_NAME': endpoint_name,
            'SQS_OUTPUT_QUEUE_NAME': output_topic_name
        }

        function_arn = self.lambda_client.create_function(
            FunctionName=name,
            Runtime='python3.8',
            Role=self.role,
            Handler='lambda_handler.lambda_handler',
            Code=dict(ZipFile=zipped_code),
            Timeout=900,
            MemorySize=500,
            Environment=dict(Variables=env_variables),
        )['FunctionArn']

        source_arn = self.sqs_client.get_queue_attributes(
            QueueUrl=input_queue_url,
            AttributeNames=['QueueArn']
        )['Attributes']['QueueArn']

        self.lambda_client.create_event_source_mapping(
            EventSourceArn=source_arn,
            FunctionName=function_arn
        )

    def delete_inference_pipeline(
            self,
            name,
            input_topic_name,
            output_topic_name,
            type='SQS'
    ):
        """
        Delete a streaming inference pipeline

        :param name: [str], Name of streaming inference
        :param input_topic_name: [str], Name of input topic name
        :param output_topic_name: [str], Name of output topic name
        :param type: [str, default='SQS'], Type of streaming inference pipeline. Only SQS is supported right now.
        """
        input_queue_url = self.sqs_client.get_queue_url(
            QueueName=input_topic_name
        )['QueueUrl']

        event_source_mapping_uuid = self.lambda_client.list_event_source_mappings(
            FunctionName=name
        )['EventSourceMappings'][0]['UUID']

        self.lambda_client.delete_event_source_mapping(
            UUID=event_source_mapping_uuid
        )

        output_queue_url = self.sqs_client.get_queue_url(
            QueueName=output_topic_name
        )['QueueUrl']

        self.sqs_client.delete_queue(
            QueueUrl=input_queue_url
        )

        self.sqs_client.delete_queue(
            QueueUrl=output_queue_url
        )

        self.lambda_client.delete_function(
            FunctionName=name
        )

    def send_to_streaming_inference(
            self,
            input_features_file,
            input_topic_name,
            type='SQS'
    ):
        """
        Send features to a streaming inference pipeline

        :param input_features_file: [str], Local path to input features file. Each line in the file is a json object.
        :param input_topic_name: [str], Name of input topic name
        :param type: [str, default='SQS'], Type of streaming inference pipeline. Only SQS is supported right now.
        """
        input_queue_url = self.sqs_client.get_queue_url(
            QueueName=input_topic_name
        )['QueueUrl']

        with open(input_features_file) as _in:
            for _str_json_obj in _in:
                self.sqs_client.send_message(
                    QueueUrl=input_queue_url,
                    MessageBody=_str_json_obj
                )

    def listen_to_streaming_inference(
            self,
            output_topic_name,
            type='SQS'
    ):
        """
        Listen to predictions in a streaming inference pipeline

        :param output_topic_name: [str], Name of output topic name
        :param type: [str, default='SQS'], Type of streaming inference pipeline. Only SQS is supported right now.
        """
        output_queue_url = self.sqs_client.get_queue_url(
            QueueName=output_topic_name
        )['QueueUrl']

        return [
            _msg['Body']
            for _msg in
            self.sqs_client.receive_message(
                QueueUrl=output_queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10
            )['Messages']
        ]
