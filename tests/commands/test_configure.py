from click.testing import CliRunner

from sagify.main import cli


def test_configure_happy_case():
    runner = CliRunner()
    result = runner.invoke(cli, ['configure'])

    assert result.exit_code == 0
