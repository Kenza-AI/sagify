import os
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

from sagify.__main__ import cli


def test_init_happy_case():
    runner = CliRunner()

    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with runner.isolated_filesystem():
            result = runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')

            assert os.path.isfile('my_app/__init__.py')
            assert os.path.isdir('my_app/sagify')
            assert os.path.isdir('my_app/sagify/training')
            assert os.path.isdir('my_app/sagify/prediction')
            assert os.path.isfile('my_app/sagify/__init__.py')
            assert os.path.isfile('my_app/sagify/build.sh')
            assert os.path.isfile('my_app/sagify/push.sh')
            assert os.path.isfile('my_app/sagify/Dockerfile')
            assert os.path.isfile('my_app/sagify/training/__init__.py')
            assert os.path.isfile('my_app/sagify/training/train')
            assert os.path.isfile('my_app/sagify/prediction/__init__.py')
            assert os.path.isfile('my_app/sagify/prediction/nginx.conf')
            assert os.path.isfile('my_app/sagify/prediction/predictor.py')
            assert os.path.isfile('my_app/sagify/prediction/wsgi.py')
            assert os.path.isfile('my_app/sagify/prediction/serve')
            assert os.path.isfile('my_app/sagify/local_test/train_local.sh')
            assert os.path.isdir('my_app/sagify/local_test/test_dir/input/data/training')
            assert os.path.isfile('my_app/sagify/local_test/test_dir/input/config/hyperparameters.json')
            assert os.path.isdir('my_app/sagify/local_test/test_dir/model')
            assert os.path.isdir('my_app/sagify/local_test/test_dir/output')

    assert result.exit_code == 0


def test_init_when_directory_already_exists():
    runner = CliRunner()
    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with runner.isolated_filesystem():
            os.makedirs('my_app/sagify')

            result = runner.invoke(
                cli=cli,
                args=['init'],
                input='my_app\n1\n2\nus-east-1\nN\nmy_sagify\n'
            )

    assert result.exit_code == -1


def test_init_when_aws_cli_is_not_configure_locally():
    runner = CliRunner()
    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=[]
    ):
        with runner.isolated_filesystem():
            result = runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\n')

    assert result.exit_code == -1
