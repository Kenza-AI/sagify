# -*- coding: utf-8 -*-
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

import sagify
from sagify.config.config import Config
from sagify.__main__ import cli


class TestUploadData(object):
    def test_upload_data_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    instance.upload_data.return_value = 's3://path-to-data/data/'
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'upload-data',
                                '-i', 'input_data/',
                                '-s', 's3://path-to-data'
                            ]
                        )
                    instance.upload_data.assert_called_with('input_data/', 's3://path-to-data')

        assert result.exit_code == 0


class TestTrain(object):
    def test_train_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'train',
                                '-i', 's3://bucket/input',
                                '-o', 's3://bucket/output',
                                '-e', 'ml.c4.2xlarge'
                            ]
                        )

                        assert instance.train.call_count == 1
                        instance.train.assert_called_with(
                            image_name='sagemaker-img:latest',
                            input_s3_data_location='s3://bucket/input',
                            train_instance_count=1,
                            train_instance_type='ml.c4.2xlarge',
                            train_volume_size=30,
                            train_max_run=24 * 60 * 60,
                            output_path='s3://bucket/output',
                            hyperparameters=None,
                            base_job_name=None,
                            job_name=None,
                            metric_names=None,
                            tags=None
                        )

        assert result.exit_code == 0

    def test_train_with_base_job_name_and_role_and_external_id_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'train',
                                '-i', 's3://bucket/input',
                                '-o', 's3://bucket/output',
                                '-e', 'ml.c4.2xlarge',
                                '-r', 'some iam role',
                                '-x', 'some external id',
                                '-n', 'some job name prefix'
                            ]
                        )

                        assert instance.train.call_count == 1
                        instance.train.assert_called_with(
                            image_name='sagemaker-img:latest',
                            input_s3_data_location='s3://bucket/input',
                            train_instance_count=1,
                            train_instance_type='ml.c4.2xlarge',
                            train_volume_size=30,
                            train_max_run=24 * 60 * 60,
                            output_path='s3://bucket/output',
                            hyperparameters=None,
                            base_job_name='some job name prefix',
                            job_name=None,
                            metric_names=None,
                            tags=None
                        )

        assert result.exit_code == 0

    def test_train_with_job_name_and_base_job_name_and_role_and_external_id_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'train',
                                '-i', 's3://bucket/input',
                                '-o', 's3://bucket/output',
                                '-e', 'ml.c4.2xlarge',
                                '-r', 'some iam role',
                                '-x', 'some external id',
                                '-n', 'some job name prefix',
                                '--job-name', 'some job name'
                            ]
                        )

                        assert instance.train.call_count == 1
                        instance.train.assert_called_with(
                            image_name='sagemaker-img:latest',
                            input_s3_data_location='s3://bucket/input',
                            train_instance_count=1,
                            train_instance_type='ml.c4.2xlarge',
                            train_volume_size=30,
                            train_max_run=24 * 60 * 60,
                            output_path='s3://bucket/output',
                            hyperparameters=None,
                            base_job_name='some job name prefix',
                            job_name='some job name',
                            metric_names=None,
                            tags=None
                        )

        assert result.exit_code == 0

    def test_train_with_tags_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'train',
                                '-i', 's3://bucket/input',
                                '-o', 's3://bucket/output',
                                '-e', 'ml.c4.2xlarge',
                                '-a', 'key1=value1;key2=2'
                            ]
                        )

                        assert instance.train.call_count == 1
                        instance.train.assert_called_with(
                            image_name='sagemaker-img:latest',
                            input_s3_data_location='s3://bucket/input',
                            train_instance_count=1,
                            train_instance_type='ml.c4.2xlarge',
                            train_volume_size=30,
                            train_max_run=24 * 60 * 60,
                            output_path='s3://bucket/output',
                            hyperparameters=None,
                            base_job_name=None,
                            job_name=None,
                            metric_names=None,
                            tags=[
                                {
                                    'Key': 'key1',
                                    'Value': 'value1',
                                },
                                {
                                    'Key': 'key2',
                                    'Value': '2',
                                },
                            ]
                        )

        assert result.exit_code == 0

    def test_train_with_docker_tag_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                '--docker-tag', 'some-docker-tag',
                                'cloud', 'train',
                                '-i', 's3://bucket/input',
                                '-o', 's3://bucket/output',
                                '-e', 'ml.c4.2xlarge'
                            ]
                        )

                        assert instance.train.call_count == 1
                        instance.train.assert_called_with(
                            image_name='sagemaker-img:some-docker-tag',
                            input_s3_data_location='s3://bucket/input',
                            train_instance_count=1,
                            train_instance_type='ml.c4.2xlarge',
                            train_volume_size=30,
                            train_max_run=24 * 60 * 60,
                            output_path='s3://bucket/output',
                            hyperparameters=None,
                            base_job_name=None,
                            job_name=None,
                            metric_names=None,
                            tags=None
                        )

        assert result.exit_code == 0


class TestDeploy(object):
    def test_deploy_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'deploy',
                                '-m', 's3://bucket/model/location/model.tar.gz',
                                '-n', '2',
                                '-e', 'ml.c4.2xlarge'
                            ]
                        )

                        assert instance.deploy.call_count == 1
                        instance.deploy.assert_called_with(
                            image_name='sagemaker-img:latest',
                            s3_model_location='s3://bucket/model/location/model.tar.gz',
                            train_instance_count=2,
                            train_instance_type='ml.c4.2xlarge',
                            tags=None
                        )

        assert result.exit_code == 0

    def test_deploy_with_role_and_external_id_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'deploy',
                                '-m', 's3://bucket/model/location/model.tar.gz',
                                '-n', '2',
                                '-e', 'ml.c4.2xlarge',
                                '-r', 'some iam role',
                                '-x', 'some external id'
                            ]
                        )

                        assert instance.deploy.call_count == 1
                        instance.deploy.assert_called_with(
                            image_name='sagemaker-img:latest',
                            s3_model_location='s3://bucket/model/location/model.tar.gz',
                            train_instance_count=2,
                            train_instance_type='ml.c4.2xlarge',
                            tags=None
                        )

        assert result.exit_code == 0

    def test_deploy_with_tags_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'deploy',
                                '-m', 's3://bucket/model/location/model.tar.gz',
                                '-n', '2',
                                '-e', 'ml.c4.2xlarge',
                                '-a', 'key1=value1;key2=2'
                            ]
                        )

                        assert instance.deploy.call_count == 1
                        instance.deploy.assert_called_with(
                            image_name='sagemaker-img:latest',
                            s3_model_location='s3://bucket/model/location/model.tar.gz',
                            train_instance_count=2,
                            train_instance_type='ml.c4.2xlarge',
                            tags=[
                                {
                                    'Key': 'key1',
                                    'Value': 'value1',
                                },
                                {
                                    'Key': 'key2',
                                    'Value': '2',
                                },
                            ]
                        )

        assert result.exit_code == 0

    def test_deploy_with_docker_tag_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                '-t', 'some-docker-tag',
                                'cloud', 'deploy',
                                '-m', 's3://bucket/model/location/model.tar.gz',
                                '-n', '2',
                                '-e', 'ml.c4.2xlarge'
                            ]
                        )

                        assert instance.deploy.call_count == 1
                        instance.deploy.assert_called_with(
                            image_name='sagemaker-img:some-docker-tag',
                            s3_model_location='s3://bucket/model/location/model.tar.gz',
                            train_instance_count=2,
                            train_instance_type='ml.c4.2xlarge',
                            tags=None
                        )

        assert result.exit_code == 0


class TestBatchTransform(object):
    def test_batch_transform_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'batch_transform',
                                '-m', 's3://bucket/model/location/model.tar.gz',
                                '-i', 's3://bucket/input_data',
                                '-o', 's3://bucket/output',
                                '-n', '2',
                                '-e', 'ml.c4.2xlarge'
                            ]
                        )

                        assert instance.batch_transform.call_count == 1
                        instance.batch_transform.assert_called_with(
                            image_name='sagemaker-img:latest',
                            s3_model_location='s3://bucket/model/location/model.tar.gz',
                            s3_input_location='s3://bucket/input_data',
                            s3_output_location='s3://bucket/output',
                            transform_instance_count=2,
                            transform_instance_type='ml.c4.2xlarge',
                            tags=None
                        )

        assert result.exit_code == 0

    def test_batch_transform_with_role_and_external_id_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'batch_transform',
                                '-m', 's3://bucket/model/location/model.tar.gz',
                                '-i', 's3://bucket/input_data',
                                '-o', 's3://bucket/output',
                                '-n', '2',
                                '-e', 'ml.c4.2xlarge',
                                '-r', 'some iam role',
                                '-x', 'some external id'
                            ]
                        )

                        assert instance.batch_transform.call_count == 1
                        instance.batch_transform.assert_called_with(
                            image_name='sagemaker-img:latest',
                            s3_model_location='s3://bucket/model/location/model.tar.gz',
                            s3_input_location='s3://bucket/input_data',
                            s3_output_location='s3://bucket/output',
                            transform_instance_count=2,
                            transform_instance_type='ml.c4.2xlarge',
                            tags=None
                        )

        assert result.exit_code == 0

    def test_batch_transform_with_tags_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'batch_transform',
                                '-m', 's3://bucket/model/location/model.tar.gz',
                                '-i', 's3://bucket/input_data',
                                '-o', 's3://bucket/output',
                                '-n', '2',
                                '-e', 'ml.c4.2xlarge',
                                '-a', 'key1=value1;key2=2'
                            ]
                        )

                        assert instance.batch_transform.call_count == 1
                        instance.batch_transform.assert_called_with(
                            image_name='sagemaker-img:latest',
                            s3_model_location='s3://bucket/model/location/model.tar.gz',
                            s3_input_location='s3://bucket/input_data',
                            s3_output_location='s3://bucket/output',
                            transform_instance_count=2,
                            transform_instance_type='ml.c4.2xlarge',
                            tags=[
                                {
                                    'Key': 'key1',
                                    'Value': 'value1',
                                },
                                {
                                    'Key': 'key2',
                                    'Value': '2',
                                },
                            ]
                        )

        assert result.exit_code == 0

    def test_batch_transform_with_docker_tag_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                '-t', 'some-docker-tag',
                                'cloud', 'batch_transform',
                                '-m', 's3://bucket/model/location/model.tar.gz',
                                '-i', 's3://bucket/input_data',
                                '-o', 's3://bucket/output',
                                '-n', '2',
                                '-e', 'ml.c4.2xlarge'
                            ]
                        )

                        assert instance.batch_transform.call_count == 1
                        instance.batch_transform.assert_called_with(
                            image_name='sagemaker-img:some-docker-tag',
                            s3_model_location='s3://bucket/model/location/model.tar.gz',
                            s3_input_location='s3://bucket/input_data',
                            s3_output_location='s3://bucket/output',
                            transform_instance_count=2,
                            transform_instance_type='ml.c4.2xlarge',
                            tags=None
                        )

        assert result.exit_code == 0


class TestHyperparameterOptimization(object):
    def test_hyperparameter_optimization_happy_case(self):
        hyperparams_ranges = """
        {
            "ParameterRanges": {
                "CategoricalParameterRanges": [
                    {
                        "Name": "kernel",
                        "Values": ["linear", "rbf"]
                    }
                ],
                "ContinuousParameterRanges": [
                {
                  "MinValue": 0.001,
                  "MaxValue": 10,
                  "Name": "gamma"
                }
                ],
                "IntegerParameterRanges": [
                    {
                        "Name": "C",
                        "MinValue": 1,
                        "MaxValue": 10
                    }
                ]
            },
            "ObjectiveMetric": {
                "Name": "Precision",
                "Type": "Maximize"
            }
        }
        """

        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6', sagify_module_dir='sage'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        with open('hyperparams_ranges.json', 'w') as f:
                            f.write(hyperparams_ranges)

                        runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'hyperparameter_optimization',
                                '-i', 's3://bucket/input',
                                '-o', 's3://bucket/output',
                                '-e', 'ml.c4.2xlarge',
                                '-h', 'hyperparams_ranges.json'
                            ]
                        )

                        assert instance.hyperparameter_optimization.call_count == 1

        assert result.exit_code == 0
