from click.testing import CliRunner

from sagify.main import cli


def test_create_endpoint_happy_case():
    runner = CliRunner()
    result = runner.invoke(cli, ['create-endpoint'])

    assert result.exit_code == 0
