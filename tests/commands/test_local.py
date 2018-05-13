try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

from sagify.__main__ import cli


class TestTrain(object):
    def test_train_happy_case(self):
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
                    result = runner.invoke(cli=cli, args=['local', 'train'])

        assert result.exit_code == 0

    def test_train_with_dir_arg_happy_case(self):
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
                    result = runner.invoke(cli=cli, args=['local', 'train', '-d', 'src/'])

        assert result.exit_code == 0

    def test_train_with_invalid_dir_arg_happy_case(self):
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
                    result = runner.invoke(cli=cli, args=['local', 'train', '-d', 'invalid_dir/'])

        assert result.exit_code == -1


class TestDeploy(object):
    def test_deploy_happy_case(self):
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
                    result = runner.invoke(cli=cli, args=['local', 'deploy'])

        assert result.exit_code == 0

    def test_deploy_with_dir_arg_happy_case(self):
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
                    result = runner.invoke(cli=cli, args=['local', 'deploy', '-d', 'src/'])

        assert result.exit_code == 0

    def test_deploy_with_invalid_dir_arg_happy_case(self):
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
                    result = runner.invoke(cli=cli, args=['local', 'deploy', '-d', 'invalid_dir/'])

        assert result.exit_code == -1
