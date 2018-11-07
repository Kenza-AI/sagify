try:
    from unittest import TestCase
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

from sagify.__main__ import cli


class PushCommandTests(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.command_line = patch('future.moves.subprocess.check_output', return_value=None).start()
        patch('sagify.commands.initialize._get_local_aws_profiles', return_value=['default', 'sagemaker']).start()

    def test_push_happy_case(self):
        assert self.runCommands(
            init_command=['init'],
            push_command=['push', '-p', 'some-profile']
            ).exit_code == 0
        self.command_line.assert_called_once_with(['sagify/push.sh', 'latest', 'some-profile'])

    def test_push_with_default_profile_happy_case(self):
        assert self.runCommands(
            init_command=['init'],
            push_command=['push']
            ).exit_code == 0
        self.command_line.assert_called_once_with(['sagify/push.sh', 'latest', None])

    def test_push_with_dir_arg_happy_case(self):
        assert self.runCommands(
            init_command=['init', '-d', 'src/'],
            push_command=['push', '-d', 'src/', '-p', 'some-profile']
            ).exit_code == 0
        self.command_line.assert_called_once_with(['src/sagify/push.sh', 'latest', 'some-profile'])

    def test_push_with_invalid_dir_arg_happy_case(self):
        assert self.runCommands(
            init_command=['init', '-d', 'src/'],
            push_command=['push', '-d', 'invalid_dir/', '-p', 'some-profile']
            ).exit_code == -1
        self.command_line.assert_not_called()

    def runCommands(self, init_command, push_command):
        runner = self.runner
        with runner.isolated_filesystem():
            runner.invoke(cli=cli, args=init_command, input='my_app\n1\n2\nus-east-1\n')
            return runner.invoke(cli=cli, args=push_command)
