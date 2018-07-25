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
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
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

    def test_upload_data_with_dir_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    instance.upload_data.return_value = 's3://path-to-data/data/'
                    with runner.isolated_filesystem():
                        runner.invoke(
                            cli=cli, args=['init', '-d', 'src/'], input='my_app\n1\n2\nus-east-1\n'
                        )
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'upload-data',
                                '-d',
                                'src/',
                                '-i', 'input_data/',
                                '-s', 's3://path-to-data'
                            ]
                        )
                    instance.upload_data.assert_called_with('input_data/', 's3://path-to-data')

        assert result.exit_code == 0

    def test_upload_data_with_invalid_dir_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    instance.upload_data.return_value = 's3://path-to-data/data/'
                    with runner.isolated_filesystem():
                        runner.invoke(
                            cli=cli, args=['init', '-d', 'src/'], input='my_app\n1\n2\nus-east-1\n'
                        )
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'upload-data',
                                '-d',
                                'invalid_dir/',
                                '-i', 'input_data/',
                                '-s', 's3://path-to-data'
                            ]
                        )
                    assert instance.upload_data.call_count == 0

        assert result.exit_code == -1


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
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
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
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
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

    def test_train_with_dir_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(
                            cli=cli, args=['init', '-d', 'src/'], input='my_app\n1\n2\nus-east-1\n'
                        )
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'train',
                                '-d',
                                'src/',
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
                            tags=None
                        )

        assert result.exit_code == 0

    def test_train_with_invalid_dir_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(
                            cli=cli, args=['init', '-d', 'src/'], input='my_app\n1\n2\nus-east-1\n'
                        )
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'train',
                                '-d',
                                'invalid_dir/',
                                '-i', 's3://bucket/input',
                                '-o', 's3://bucket/output',
                                '-e', 'ml.c4.2xlarge'
                            ]
                        )

                        assert not instance.train.called

        assert result.exit_code == -1


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
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
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

    def test_deploy_with_dir_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(
                            cli=cli, args=['init', '-d', 'src/'], input='my_app\n1\n2\nus-east-1\n'
                        )
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'deploy',
                                '-d',
                                'src/',
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
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
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

    def test_deploy_with_invalid_dir_arg_happy_case(self):
        runner = CliRunner()

        with patch(
                'sagify.commands.initialize._get_local_aws_profiles',
                return_value=['default', 'sagify']
        ):
            with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1'
                    )
            ):
                with patch(
                        'sagify.sagemaker.sagemaker.SageMakerClient'
                ) as mocked_sage_maker_client:
                    instance = mocked_sage_maker_client.return_value
                    with runner.isolated_filesystem():
                        runner.invoke(
                            cli=cli, args=['init', '-d', 'src/'], input='my_app\n1\n2\nus-east-1\n'
                        )
                        result = runner.invoke(
                            cli=cli,
                            args=[
                                'cloud', 'deploy',
                                '-d',
                                'invalid_dir/',
                                '-m', 's3://bucket/model/location/model.tar.gz',
                                '-n', '2',
                                '-e', 'ml.c4.2xlarge'
                            ]
                        )

                        assert not instance.deploy.called

        assert result.exit_code == -1
