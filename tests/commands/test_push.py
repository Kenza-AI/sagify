from collections import namedtuple

try:
    from unittest import TestCase
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

from sagify.__main__ import cli

Case = namedtuple('Case', 'description, init_cmd, push_cmd, expected_exit_code, expected_cli_call')

push_script_path = 'my_app/sagify/push.sh'

t1 = Case('t1: sagify push', ['init'], ['push'], 0,
          lambda command_line: command_line.assert_called_once_with([push_script_path, 'latest', 'us-east-1', '', 'sagemaker', '', 'my_app']))

t2 = Case('t2: sagify push -p profile', ['init'], ['push', '-p', 'some-profile'], 0,
          lambda command_line: command_line.assert_called_once_with([push_script_path, 'latest', 'us-east-1', '', 'some-profile', '', 'my_app']))

t3 = Case('t3: sagify push -r region', ['init'], ['push', '-r', 'some-region'], 0,
          lambda command_line: command_line.assert_called_once_with([push_script_path, 'latest', 'some-region', '', 'sagemaker', '', 'my_app']))

t4 = Case('t4: sagify push -r region -p profile', ['init'], ['push', '-r', 'some-region', '-p', 'prof'], 0,
          lambda command_line: command_line.assert_called_once_with([push_script_path, 'latest', 'some-region', '', 'prof', '', 'my_app']))

t5 = Case('t5: sagify push -i aws-role', ['init'], ['push', '-i', 'some-role-arn'], 0,
          lambda command_line: command_line.assert_called_once_with([push_script_path, 'latest', 'us-east-1', 'some-role-arn', '', '', 'my_app']))

t6 = Case('t6: sagify -p profile -i aws-role', ['init'], ['push', '-i', 'some-role-arn', '-p', 'some-profile'], 2,
          lambda command_line: command_line.assert_not_called())

t7 = Case('t7: sagify push -i aws-role -e some-id', ['init'], ['push', '-i', 'some-role-arn', '-e', 'some-id'], 0,
          lambda command_line:
          command_line.assert_called_once_with([push_script_path, 'latest', 'us-east-1', 'some-role-arn', '', 'some-id', 'my_app']))

test_cases = [t1, t2, t3, t4, t5, t6, t7]

# Mocks
command_line_mock = patch('future.moves.subprocess.check_output', return_value=None)
patch('sagify.commands.initialize._get_local_aws_profiles', return_value=['default', 'sagemaker']).start()


class PushCommandTests(TestCase):

    def tests(self):
        for case in test_cases:
            command_line = command_line_mock.start()

            try:
                assert runCommands(case.init_cmd, case.push_cmd).exit_code == case.expected_exit_code
                case.expected_cli_call(command_line)
            except AssertionError as e:
                e.args = ('Test Case: {}'.format(case.description), e.args)
                raise

            command_line.stop()


def runCommands(init_command, push_command):
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(cli=cli, args=init_command, input='my_app\n1\n2\nus-east-1\n')
        return runner.invoke(cli=cli, args=push_command)
