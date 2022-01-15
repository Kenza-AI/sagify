# -*- coding: utf-8 -*-
import os

from sagemaker.parameter import ContinuousParameter, CategoricalParameter

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
                            hyperparameters={'n_estimator': 3},
                            base_job_name="Some-job-name-prefix",
                            job_name="some job name"
                        )
                        mocked_sagemaker_estimator.assert_called_with(
                            image_uri='image-full-name',
                            role='arn_role',
                            instance_count=1,
                            instance_type='m1.xlarge',
                            volume_size=30,
                            max_run=60,
                            input_mode='File',
                            base_job_name="Some-job-name-prefix",
                            output_path='s3://bucket/output',
                            hyperparameters={'n_estimator': 3},
                            sagemaker_session=sagemaker_session_instance,
                            metric_definitions=None,
                            use_spot_instances=False,
                            max_wait=None
                        )
                        sagemaker_estimator_instance = mocked_sagemaker_estimator.return_value
                        assert sagemaker_estimator_instance.fit.call_count == 1
                        sagemaker_estimator_instance.fit.assert_called_with('s3://bucket/input', job_name='some job name')


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
                            image_uri='image-full-name',
                            role='arn_role',
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_model_instance = mocked_sagemaker_model.return_value
                        assert sagemaker_model_instance.deploy.call_count == 1
                        sagemaker_model_instance.deploy.assert_called_with(
                            initial_instance_count=1,
                            instance_type='m1.xlarge',
                            tags=None,
                            endpoint_name=None
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
                            image_uri='image-full-name',
                            role='arn_role',
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_model_instance = mocked_sagemaker_model.return_value
                        assert sagemaker_model_instance.deploy.call_count == 1
                        sagemaker_model_instance.deploy.assert_called_with(
                            initial_instance_count=1,
                            instance_type='m1.xlarge',
                            tags=tags,
                            endpoint_name=None
                        )


def test_deploy_with_custom_endpoint_name():
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
                            train_instance_type='m1.xlarge',
                            endpoint_name='my-endpoint'
                        )
                        mocked_sagemaker_model.assert_called_with(
                            model_data='s3://bucket/model_input/model.tar.gz',
                            image_uri='image-full-name',
                            role='arn_role',
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_model_instance = mocked_sagemaker_model.return_value
                        assert sagemaker_model_instance.deploy.call_count == 1
                        sagemaker_model_instance.deploy.assert_called_with(
                            initial_instance_count=1,
                            instance_type='m1.xlarge',
                            tags=None,
                            endpoint_name='my-endpoint'
                        )


def test_batch_transform_happy_case():
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
                        sage_maker_client.batch_transform(
                            image_name='image',
                            s3_model_location='s3://bucket/model_input/model.tar.gz',
                            s3_input_location='s3://bucket/input_data',
                            s3_output_location='s3://bucket/output_data',
                            transform_instance_count=1,
                            transform_instance_type='m1.xlarge'
                        )
                        mocked_sagemaker_model.assert_called_with(
                            model_data='s3://bucket/model_input/model.tar.gz',
                            image_uri='image-full-name',
                            role='arn_role',
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_model_instance = mocked_sagemaker_model.return_value
                        assert sagemaker_model_instance.transformer.call_count == 1
                        sagemaker_model_instance.transformer.assert_called_with(
                            instance_type='m1.xlarge',
                            instance_count=1,
                            assemble_with='Line',
                            output_path='s3://bucket/output_data',
                            tags=None,
                            accept='application/json',
                            strategy="SingleRecord"
                        )

                        transformer = sagemaker_model_instance.transformer.return_value
                        assert transformer.transform.call_count == 1
                        transformer.transform.assert_called_with(
                            data='s3://bucket/input_data',
                            split_type='Line',
                            content_type='application/json',
                            job_name=None
                        )


def test_batch_transform_with_job_name_happy_case():
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
                        sage_maker_client.batch_transform(
                            image_name='image',
                            s3_model_location='s3://bucket/model_input/model.tar.gz',
                            s3_input_location='s3://bucket/input_data',
                            s3_output_location='s3://bucket/output_data',
                            transform_instance_count=1,
                            transform_instance_type='m1.xlarge',
                            job_name='some=job-name'
                        )
                        mocked_sagemaker_model.assert_called_with(
                            model_data='s3://bucket/model_input/model.tar.gz',
                            image_uri='image-full-name',
                            role='arn_role',
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_model_instance = mocked_sagemaker_model.return_value
                        assert sagemaker_model_instance.transformer.call_count == 1
                        sagemaker_model_instance.transformer.assert_called_with(
                            instance_type='m1.xlarge',
                            instance_count=1,
                            assemble_with='Line',
                            output_path='s3://bucket/output_data',
                            tags=None,
                            accept='application/json',
                            strategy="SingleRecord"
                        )

                        transformer = sagemaker_model_instance.transformer.return_value
                        assert transformer.transform.call_count == 1
                        transformer.transform.assert_called_with(
                            data='s3://bucket/input_data',
                            split_type='Line',
                            content_type='application/json',
                            job_name='some=job-name'
                        )


def test_batch_transform_wait_happy_case():
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
                        sage_maker_client.batch_transform(
                            image_name='image',
                            s3_model_location='s3://bucket/model_input/model.tar.gz',
                            s3_input_location='s3://bucket/input_data',
                            s3_output_location='s3://bucket/output_data',
                            transform_instance_count=1,
                            transform_instance_type='m1.xlarge',
                            wait=True
                        )
                        mocked_sagemaker_model.assert_called_with(
                            model_data='s3://bucket/model_input/model.tar.gz',
                            image_uri='image-full-name',
                            role='arn_role',
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_model_instance = mocked_sagemaker_model.return_value
                        assert sagemaker_model_instance.transformer.call_count == 1
                        sagemaker_model_instance.transformer.assert_called_with(
                            instance_type='m1.xlarge',
                            instance_count=1,
                            assemble_with='Line',
                            output_path='s3://bucket/output_data',
                            tags=None,
                            accept='application/json',
                            strategy="SingleRecord"
                        )

                        transformer = sagemaker_model_instance.transformer.return_value
                        assert transformer.transform.call_count == 1
                        transformer.transform.assert_called_with(
                            data='s3://bucket/input_data',
                            split_type='Line',
                            content_type='application/json',
                            job_name=None
                        )

                        assert transformer.wait.call_count == 1


def test_batch_transform_with_tags():
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

                        sage_maker_client.batch_transform(
                            image_name='image',
                            s3_model_location='s3://bucket/model_input/model.tar.gz',
                            s3_input_location='s3://bucket/input_data',
                            s3_output_location='s3://bucket/output_data',
                            transform_instance_count=1,
                            transform_instance_type='m1.xlarge',
                            tags=tags
                        )
                        mocked_sagemaker_model.assert_called_with(
                            model_data='s3://bucket/model_input/model.tar.gz',
                            image_uri='image-full-name',
                            role='arn_role',
                            sagemaker_session=sagemaker_session_instance
                        )
                        sagemaker_model_instance = mocked_sagemaker_model.return_value
                        assert sagemaker_model_instance.transformer.call_count == 1
                        sagemaker_model_instance.transformer.assert_called_with(
                            instance_type='m1.xlarge',
                            instance_count=1,
                            assemble_with='Line',
                            output_path='s3://bucket/output_data',
                            tags=tags,
                            accept='application/json',
                            strategy="SingleRecord"
                        )

                        transformer = sagemaker_model_instance.transformer.return_value
                        assert transformer.transform.call_count == 1
                        transformer.transform.assert_called_with(
                            data='s3://bucket/input_data',
                            split_type='Line',
                            content_type='application/json',
                            job_name=None
                        )


def test_hyperparameter_optimization_happy_case():
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
                        with patch(
                                'sagemaker.tuner.HyperparameterTuner'
                        ) as mocked_sagemaker_tuner:
                            sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')
                            sage_maker_client.hyperparameter_optimization(
                                image_name='image',
                                input_s3_data_location='s3://bucket/input',
                                instance_count=1,
                                instance_type='m1.xlarge',
                                volume_size=30,
                                max_run=60,
                                max_jobs=3,
                                max_parallel_jobs=2,
                                output_path='s3://bucket/output',
                                objective_type='Maximize',
                                objective_metric_name='Precision',
                                hyperparams_ranges_dict={
                                    'lr': ContinuousParameter(0.001, 0.1),
                                    'batch-size': CategoricalParameter([32, 64, 128, 256, 512])
                                },
                                base_job_name="Some-job-name-prefix",
                                job_name="some job name"
                            )
                            mocked_sagemaker_estimator.assert_called_with(
                                image_uri='image-full-name',
                                role='arn_role',
                                instance_count=1,
                                instance_type='m1.xlarge',
                                volume_size=30,
                                max_run=60,
                                input_mode='File',
                                output_path='s3://bucket/output',
                                sagemaker_session=sagemaker_session_instance,
                                use_spot_instances=False,
                                max_wait=None
                            )

                            mocked_sagemaker_tuner_instance = mocked_sagemaker_tuner.return_value
                            assert mocked_sagemaker_tuner_instance.fit.call_count == 1
                            mocked_sagemaker_tuner_instance.fit.assert_called_with(
                                's3://bucket/input', job_name='some job name'
                            )


def test_deploy_sklearn_happy_case():
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
                        'sagemaker.sklearn.model.SKLearnModel'
                ) as mocked_sagemaker_sklearn_model:
                    sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')
                    sage_maker_client.deploy_sklearn(
                        s3_model_location='s3://bucket/model_input/model.tar.gz',
                        instance_count=1,
                        instance_type='m1.xlarge',
                        framework_version='0.23-1'
                    )

                    mocked_sagemaker_sklearn_model.assert_called_with(
                        role='arn_role',
                        model_data='s3://bucket/model_input/model.tar.gz',
                        framework_version='0.23-1',
                        py_version='py3',
                        entry_point='sklearn_inference.py',
                        source_dir=os.path.join(sagemaker._FILE_DIR_PATH, 'sklearn_code'),
                        model_server_workers=None,
                        sagemaker_session=sagemaker_session_instance
                    )
                    sagemaker_model_instance = mocked_sagemaker_sklearn_model.return_value
                    assert sagemaker_model_instance.deploy.call_count == 1
                    sagemaker_model_instance.deploy.assert_called_with(
                        initial_instance_count=1,
                        instance_type='m1.xlarge',
                        tags=None,
                        endpoint_name=None
                    )


def test_deploy_sklearn_with_model_server_workers():
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
                        'sagemaker.sklearn.model.SKLearnModel'
                ) as mocked_sagemaker_sklearn_model:
                    sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')
                    sage_maker_client.deploy_sklearn(
                        s3_model_location='s3://bucket/model_input/model.tar.gz',
                        instance_count=1,
                        instance_type='m1.xlarge',
                        framework_version='0.23-1',
                        model_server_workers=2
                    )

                    mocked_sagemaker_sklearn_model.assert_called_with(
                        role='arn_role',
                        model_data='s3://bucket/model_input/model.tar.gz',
                        framework_version='0.23-1',
                        py_version='py3',
                        entry_point='sklearn_inference.py',
                        source_dir=os.path.join(sagemaker._FILE_DIR_PATH, 'sklearn_code'),
                        model_server_workers=2,
                        sagemaker_session=sagemaker_session_instance
                    )
                    sagemaker_model_instance = mocked_sagemaker_sklearn_model.return_value
                    assert sagemaker_model_instance.deploy.call_count == 1
                    sagemaker_model_instance.deploy.assert_called_with(
                        initial_instance_count=1,
                        instance_type='m1.xlarge',
                        tags=None,
                        endpoint_name=None
                    )


def test_deploy_hugging_face_happy_case():
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
                        'sagemaker.huggingface.HuggingFaceModel'
                ) as mocked_sagemaker_hf_model:
                    sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')

                    sage_maker_client.deploy_hugging_face(
                        s3_model_location='s3://bucket/model_input/model.tar.gz',
                        instance_count=1,
                        instance_type='m1.xlarge',
                        transformers_version='4.6.1',
                        pytorch_version='1.7.1'
                    )

                    mocked_sagemaker_hf_model.assert_called_with(
                        role='arn_role',
                        model_data='s3://bucket/model_input/model.tar.gz',
                        transformers_version='4.6.1',
                        pytorch_version='1.7.1',
                        tensorflow_version=None,
                        model_server_workers=None,
                        py_version='py36',
                        env=None,
                        sagemaker_session=sagemaker_session_instance
                    )
                    sagemaker_model_instance = mocked_sagemaker_hf_model.return_value
                    assert sagemaker_model_instance.deploy.call_count == 1
                    sagemaker_model_instance.deploy.assert_called_with(
                        initial_instance_count=1,
                        instance_type='m1.xlarge',
                        tags=None,
                        endpoint_name=None
                    )


def test_deploy_hugging_face_with_hub():
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
                        'sagemaker.huggingface.HuggingFaceModel'
                ) as mocked_sagemaker_hf_model:
                    sage_maker_client = sagemaker.SageMakerClient('sagemaker', 'us-east-1')

                    hub = {
                        'HF_MODEL_ID': 'gpt2',
                        'HF_TASK': 'text-generation'
                    }

                    sage_maker_client.deploy_hugging_face(
                        instance_count=1,
                        instance_type='m1.xlarge',
                        transformers_version='4.6.1',
                        pytorch_version='1.7.1',
                        hub=hub
                    )

                    mocked_sagemaker_hf_model.assert_called_with(
                        role='arn_role',
                        model_data=None,
                        transformers_version='4.6.1',
                        pytorch_version='1.7.1',
                        tensorflow_version=None,
                        model_server_workers=None,
                        py_version='py36',
                        env=hub,
                        sagemaker_session=sagemaker_session_instance
                    )
                    sagemaker_model_instance = mocked_sagemaker_hf_model.return_value
                    assert sagemaker_model_instance.deploy.call_count == 1
                    sagemaker_model_instance.deploy.assert_called_with(
                        initial_instance_count=1,
                        instance_type='m1.xlarge',
                        tags=None,
                        endpoint_name=None
                    )
