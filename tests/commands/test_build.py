try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

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
                runner.invoke(cli=cli, args=['init'], input='my_app\ny\n1\n2\nus-east-1\nrequirements.txt\n')
                result = runner.invoke(cli=cli, args=['build'])

    assert result.exit_code == 0
