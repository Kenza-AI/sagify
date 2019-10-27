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
            result = runner.invoke(cli=cli, args=['init'], input='my_app\ny\n1\n2\nus-east-1\nrequirements.txt\n')

            assert os.path.isfile('src/__init__.py')
            assert os.path.isdir('src/sagify')
            assert os.path.isdir('src/sagify/training')
            assert os.path.isdir('src/sagify/prediction')
            assert os.path.isfile('src/sagify/__init__.py')
            assert os.path.isfile('src/sagify/build.sh')
            assert os.path.isfile('src/sagify/push.sh')
            assert os.path.isfile('src/sagify/Dockerfile')
            assert os.path.isfile('src/sagify/training/__init__.py')
            assert os.path.isfile('src/sagify/training/train')
            assert os.path.isfile('src/sagify/training/training.py')
            assert os.path.isfile('src/sagify/prediction/__init__.py')
            assert os.path.isfile('src/sagify/prediction/nginx.conf')
            assert os.path.isfile('src/sagify/prediction/predictor.py')
            assert os.path.isfile('src/sagify/prediction/prediction.py')
            assert os.path.isfile('src/sagify/prediction/wsgi.py')
            assert os.path.isfile('src/sagify/prediction/serve')
            assert os.path.isfile('src/sagify/local_test/train_local.sh')
            assert os.path.isdir('src/sagify/local_test/test_dir/input/data/training')
            assert os.path.isfile('src/sagify/local_test/test_dir/input/config/hyperparameters.json')
            assert os.path.isdir('src/sagify/local_test/test_dir/model')
            assert os.path.isdir('src/sagify/local_test/test_dir/output')

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
                input='my_app\nN\nmy_app\n1\n2\nus-east-1\nrequirements.txt\n'
            )

    assert result.exit_code == -1


def test_init_when_aws_cli_is_not_configure_locally():
    runner = CliRunner()
    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=[]
    ):
        with runner.isolated_filesystem():
            result = runner.invoke(cli=cli, args=['init'], input='my_app\ny\n1\n2\nrequirements.txt\n')

    assert result.exit_code == -1
