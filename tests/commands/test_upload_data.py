from click.testing import CliRunner

from sagify.main import cli


def test_upload_data_happy_case():
    runner = CliRunner()
    result = runner.invoke(cli, ['upload-data'])

    assert result.exit_code == 0
