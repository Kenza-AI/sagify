from sagify.sagemaker import sagemaker


def batch_inference(
    model,
    s3_input_location,
    s3_output_location,
    aws_profile,
    aws_region,
    num_instances,
    ec2_type,
    aws_role=None,
    external_id=None,
    tags=None,
    wait=True,
    job_name=None,
    model_version='1.*',
    max_concurrent_transforms=None,
    aws_access_key_id=None,
    aws_secret_access_key=None,
):
    """
    Executes a batch inference job given a foundation model on SageMaker

    :param model: [str], model name
    :param s3_model_location: [str], S3 model location
    :param s3_input_location: [str], S3 input data location
    :param s3_output_location: [str], S3 location to save predictions
    :param aws_profile: [str], AWS profile name
    :param aws_region: [str], AWS region
    :param num_instances: [int], number of ec2 instances
    :param ec2_type: [str], ec2 instance type. Refer to:
    https://aws.amazon.com/sagemaker/pricing/instance-types/
    :param aws_role: [str, default=None], the AWS role assumed by SageMaker while deploying
    :param external_id: [str, default=None], Optional external id used when using an IAM role
    :param tags: [optional[list[dict], default=None], default: None], List of tags for labeling a training
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
    :param wait: [bool, default=True], wait or not for the batch transform to finish
    :param job_name: [str, default=None], name for the SageMaker batch transform job
    :param model_version: [str, default='1.*'], model version to use
    :param max_concurrent_transforms: [int, default=None], max number of concurrent transforms
    :param aws_access_key_id: [str, default=None], AWS access key id
    :param aws_secret_access_key: [str, default=None], AWS secret access key

    :return: [str], transform job status if wait=True.
    Valid values: 'InProgress'|'Completed'|'Failed'|'Stopping'|'Stopped'
    """
    sage_maker_client = sagemaker.SageMakerClient(
        aws_profile=aws_profile,
        aws_region=aws_region,
        aws_role=aws_role,
        external_id=external_id,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    return sage_maker_client.foundation_model_batch_transform(
        model_id=model,
        s3_input_location=s3_input_location,
        s3_output_location=s3_output_location,
        num_instances=num_instances,
        ec2_type=ec2_type,
        max_concurrent_transforms=max_concurrent_transforms,
        tags=tags,
        wait=wait,
        job_name=job_name,
        model_version=model_version
    )
