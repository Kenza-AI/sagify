import json
import os

import boto3

sagemaker_client = boto3.client('sagemaker-runtime', region_name=os.environ.get('REGION_NAME'))
sqs_client = boto3.client('sqs', region_name=os.environ.get('REGION_NAME'))


def lambda_handler(event, context):
    records = event['Records']
    for item in records:
        response = sagemaker_client.invoke_endpoint(
            EndpointName=os.environ.get('SAGEMAKER_ENDPOINT_NAME'),
            Body=item["body"],
            ContentType='application/json'
        )

        sqs_queue_url = sqs_client.get_queue_url(
            QueueName=os.environ.get('SQS_OUTPUT_QUEUE_NAME')
        )['QueueUrl']

        sqs_client.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps(json.loads(response['Body'].read()))
        )

    return {
        'statusCode': 200,
        'body': str(len(records)) + ' processed'
    }
