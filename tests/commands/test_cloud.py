try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

import sagify
from sagify.config.config import Config
from sagify.main import cli


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
