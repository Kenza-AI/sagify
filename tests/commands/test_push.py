try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

from sagify.__main__ import cli


def test_push_happy_case():
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
                result = runner.invoke(cli=cli, args=['push'])

    assert result.exit_code == 0


def test_push_with_dir_arg_happy_case():
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
                result = runner.invoke(cli=cli, args=['push', '-d', 'src/'])

    assert result.exit_code == 0


def test_push_with_invalid_dir_arg_happy_case():
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
                result = runner.invoke(cli=cli, args=['push', '-d', 'invalid_dir/'])

    assert result.exit_code == -1
