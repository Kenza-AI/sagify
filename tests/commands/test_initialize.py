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
            result = runner.invoke(cli=cli, args=['init'], input='my_app\ny\n1\n1\nus-east-1\nrequirements.txt\n')

            assert os.path.isfile('src/__init__.py')
            assert os.path.isdir('src/sagify_base')
            assert os.path.isdir('src/sagify_base/training')
            assert os.path.isdir('src/sagify_base/prediction')
            assert os.path.isfile('src/sagify_base/__init__.py')
            assert os.path.isfile('src/sagify_base/build.sh')
            assert os.path.isfile('src/sagify_base/push.sh')
            assert os.path.isfile('src/sagify_base/Dockerfile')
            assert os.path.isfile('src/sagify_base/training/__init__.py')
            assert os.path.isfile('src/sagify_base/training/train')
            assert os.path.isfile('src/sagify_base/training/training.py')
            assert os.path.isfile('src/sagify_base/prediction/__init__.py')
            assert os.path.isfile('src/sagify_base/prediction/nginx.conf')
            assert os.path.isfile('src/sagify_base/prediction/predictor.py')
            assert os.path.isfile('src/sagify_base/prediction/prediction.py')
            assert os.path.isfile('src/sagify_base/prediction/wsgi.py')
            assert os.path.isfile('src/sagify_base/prediction/serve')
            assert os.path.isfile('src/sagify_base/local_test/train_local.sh')
            assert os.path.isdir('src/sagify_base/local_test/test_dir/input/data/training')
            assert os.path.isfile('src/sagify_base/local_test/test_dir/input/config/hyperparameters.json')
            assert os.path.isdir('src/sagify_base/local_test/test_dir/model')
            assert os.path.isdir('src/sagify_base/local_test/test_dir/output')

    assert result.exit_code == 0


def test_init_when_directory_already_exists():
    runner = CliRunner()
    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with runner.isolated_filesystem():
            os.makedirs('my_app/sagify_base')

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

    assert result.exit_code == 1
