try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

import sagify
from sagify.config.config import Config
from sagify.__main__ import cli


def test_build_happy_case():
    runner = CliRunner()

    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with patch(
                'future.moves.subprocess.check_output',
                return_value=None
        ):
            with runner.isolated_filesystem():
                runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')
                result = runner.invoke(cli=cli, args=['build', '-r', 'requirements.txt'])

    assert result.exit_code == 0


def test_build_with_dir_arg_happy_case():
    runner = CliRunner()

    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with patch(
                'future.moves.subprocess.check_output',
                return_value=None
        ):
            with runner.isolated_filesystem():
                runner.invoke(
                    cli=cli, args=['init', '-d', 'src/'], input='my_app\n1\n2\nus-east-1\n'
                )
                result = runner.invoke(
                    cli=cli, args=['build', '-d', 'src/', '-r', 'requirements.txt']
                )

    assert result.exit_code == 0


def test_build_with_invalid_dir_arg():
    runner = CliRunner()

    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with patch.object(
                    sagify.config.config.ConfigManager,
                    'get_config',
                    lambda _: Config(
                        image_name='sagemaker-img', aws_profile='sagify', aws_region='us-east-1', python_version='3.6'
                    )
        ):
            with runner.isolated_filesystem():
                runner.invoke(
                    cli=cli, args=['init', '-d', 'src/'], input='my_app\n1\n2\nus-east-1\n'
                )
                result = runner.invoke(
                    cli=cli, args=['build', '-d', 'invalid_dir/', '-r', 'requirements.txt']
                )

    assert result.exit_code == -1
