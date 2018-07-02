try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from sagify.sagemaker import sagemaker


def test_upload_data_happy_case():
    with patch(
            'boto3.Session'
    ):
        with patch(
                'sagemaker.Session'
        ) as mocked_sagemaker_session:
            sagemaker_session_instance = mocked_sagemaker_session.return_value

            with patch(
                    'sagemaker.get_execution_role',
                    return_value='arn_role'
            ):
                sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')
                sage_maker_client.upload_data(
                    input_dir='/input/data',
                    s3_dir='s3://bucket/input_data'
                )
                assert sagemaker_session_instance.upload_data.call_count == 1
                sagemaker_session_instance.upload_data.assert_called_with(
                    path='/input/data',
                    bucket='bucket',
                    key_prefix='input_data'
                )


def test_upload_data_with_s3_path_that_contains_only_bucket_name():
    with patch(
            'boto3.Session'
    ):
        with patch(
                'sagemaker.Session'
        ) as mocked_sagemaker_session:
            sagemaker_session_instance = mocked_sagemaker_session.return_value

            with patch(
                    'sagemaker.get_execution_role',
                    return_value='arn_role'
            ):
                sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')
                sage_maker_client.upload_data(
                    input_dir='/input/data',
                    s3_dir='s3://bucket/'
                )
                assert sagemaker_session_instance.upload_data.call_count == 1
                sagemaker_session_instance.upload_data.assert_called_with(
                    path='/input/data',
                    bucket='bucket',
                    key_prefix='data'
                )


def test_train_happy_case():
    with patch(
            'boto3.Session'
    ):
        with patch(
                'sagemaker.Session'
        ) as mocked_sagemaker_session:
            sagemaker_session_instance = mocked_sagemaker_session.return_value

            with patch(
                    'sagemaker.get_execution_role',
                    return_value='arn_role'
            ):
                with patch(
                        'sagemaker.estimator.Estimator'
                ) as mocked_sagemaker_estimator:
                    with patch(
                            'sagify.sagemaker.sagemaker.SageMakerClient._construct_image_location',
                            return_value='image-full-name'
                    ):
                        sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')
                        sage_maker_client.train(
                            image_name='image',
                            input_s3_data_location='s3://bucket/input',
                            train_instance_count=1,
                            train_instance_type='m1.xlarge',
                            train_volume_size=30,
                            train_max_run=60,
                            output_path='s3://bucket/output',
                            hyperparameters={'n_estimator': 3}
                        )
                        mocked_sagemaker_estimator.assert_called_with(
                            image_name='image-full-name',
                            role='arn_role',
                            train_instance_count=1,
                            train_instance_type='m1.xlarge',
                            train_volume_size=30,
                            train_max_run=60,
                            input_mode='File',
                            output_path='s3://bucket/output',
                            hyperparameters={'n_estimator': 3},
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_estimator_instance = mocked_sagemaker_estimator.return_value
                        assert sagemaker_estimator_instance.fit.call_count == 1
                        sagemaker_estimator_instance.fit.assert_called_with('s3://bucket/input')


def test_deploy_happy_case():
    with patch(
            'boto3.Session'
    ):
        with patch(
                'sagemaker.Session'
        ) as mocked_sagemaker_session:
            sagemaker_session_instance = mocked_sagemaker_session.return_value

            with patch(
                    'sagemaker.get_execution_role',
                    return_value='arn_role'
            ):
                with patch(
                        'sagemaker.Model'
                ) as mocked_sagemaker_model:
                    with patch(
                            'sagify.sagemaker.sagemaker.SageMakerClient._construct_image_location',
                            return_value='image-full-name'
                    ):
                        sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')
                        sage_maker_client.deploy(
                            image_name='image',
                            s3_model_location='s3://bucket/model_input/model.tar.gz',
                            train_instance_count=1,
                            train_instance_type='m1.xlarge'
                        )
                        mocked_sagemaker_model.assert_called_with(
                            model_data='s3://bucket/model_input/model.tar.gz',
                            image='image-full-name',
                            role='arn_role',
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_model_instance = mocked_sagemaker_model.return_value
                        assert sagemaker_model_instance.deploy.call_count == 1
                        sagemaker_model_instance.deploy.assert_called_with(
                            initial_instance_count=1,
                            instance_type='m1.xlarge',
                            tags=None
                        )


def test_deploy_with_tags():
    with patch(
            'boto3.Session'
    ):
        with patch(
                'sagemaker.Session'
        ) as mocked_sagemaker_session:
            sagemaker_session_instance = mocked_sagemaker_session.return_value

            with patch(
                    'sagemaker.get_execution_role',
                    return_value='arn_role'
            ):
                with patch(
                        'sagemaker.Model'
                ) as mocked_sagemaker_model:
                    with patch(
                            'sagify.sagemaker.sagemaker.SageMakerClient._construct_image_location',
                            return_value='image-full-name'
                    ):
                        sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')

                        tags = [
                            {
                                'Key': 'key_name_1',
                                'Value': 1,
                            },
                            {
                                'Key': 'key_name_2',
                                'Value': '2',
                            },
                        ]

                        sage_maker_client.deploy(
                            image_name='image',
                            s3_model_location='s3://bucket/model_input/model.tar.gz',
                            train_instance_count=1,
                            train_instance_type='m1.xlarge',
                            tags=tags
                        )
                        mocked_sagemaker_model.assert_called_with(
                            model_data='s3://bucket/model_input/model.tar.gz',
                            image='image-full-name',
                            role='arn_role',
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_model_instance = mocked_sagemaker_model.return_value
                        assert sagemaker_model_instance.deploy.call_count == 1
                        sagemaker_model_instance.deploy.assert_called_with(
                            initial_instance_count=1,
                            instance_type='m1.xlarge',
                            tags=tags
                        )
