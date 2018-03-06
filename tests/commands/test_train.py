from click.testing import CliRunner

from sagify.main import cli


def test_train_happy_case():
    runner = CliRunner()
    result = runner.invoke(cli, ['train'])

    assert result.exit_code == 0
