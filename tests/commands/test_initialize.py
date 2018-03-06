from click.testing import CliRunner

from sagify.main import cli


def test_init_happy_case():
    runner = CliRunner()
    result = runner.invoke(cli, ['init'])

    assert result.exit_code == 0


def test_init_with_single_letter_dir_arg_happy_case():
    runner = CliRunner()
    result = runner.invoke(cli, ['init', '-d', 'src/'])

    assert result.exit_code == 0


def test_init_with_long_dir_arg_happy_case():
    runner = CliRunner()
    result = runner.invoke(cli, ['init', '--dir', 'src/'])

    assert result.exit_code == 0
