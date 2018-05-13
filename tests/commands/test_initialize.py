import os
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest
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

            assert os.path.isfile('__init__.py')
            assert os.path.isdir('sagify')
            assert os.path.isdir('sagify/training')
            assert os.path.isdir('sagify/prediction')
            assert os.path.isfile('sagify/__init__.py')
            assert os.path.isfile('sagify/build.sh')
            assert os.path.isfile('sagify/push.sh')
            assert os.path.isfile('sagify/Dockerfile')
            assert os.path.isfile('sagify/training/__init__.py')
            assert os.path.isfile('sagify/training/train')
            assert os.path.isfile('sagify/prediction/__init__.py')
            assert os.path.isfile('sagify/prediction/nginx.conf')
            assert os.path.isfile('sagify/prediction/predictor.py')
            assert os.path.isfile('sagify/prediction/wsgi.py')
            assert os.path.isfile('sagify/prediction/serve')
            assert os.path.isfile('sagify/local_test/train_local.sh')
            assert os.path.isdir('sagify/local_test/test_dir/input/data/training')
            assert os.path.isfile('sagify/local_test/test_dir/input/config/hyperparameters.json')
            assert os.path.isdir('sagify/local_test/test_dir/model')
            assert os.path.isdir('sagify/local_test/test_dir/output')

    assert result.exit_code == 0


@pytest.mark.parametrize("test_input_args", [
    ['init', '-d', 'src/'],
    ['init', '--dir', 'my_app/']
])
def test_init_with_dir_arg_happy_case(test_input_args):
    runner = CliRunner()

    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli=cli,
                args=test_input_args,
                input='my_app\n1\n2\nus-east-1\n'
            )

            root_dir = test_input_args[2]

            assert os.path.isfile(os.path.join(root_dir, '__init__.py'))
            assert os.path.isdir(os.path.join(root_dir, 'sagify'))
            assert os.path.isdir(os.path.join(root_dir, 'sagify/training'))
            assert os.path.isdir(os.path.join(root_dir, 'sagify/prediction'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/__init__.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/build.sh'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/push.sh'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/Dockerfile'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/training/__init__.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/training/train'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/__init__.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/nginx.conf'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/predictor.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/wsgi.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/serve'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/local_test/train_local.sh'))
            assert os.path.isdir(
                os.path.join(root_dir, 'sagify/local_test/test_dir/input/data/training')
            )
            assert os.path.isfile(
                os.path.join(
                    root_dir,
                    'sagify/local_test/test_dir/input/config/hyperparameters.json'
                )
            )
            assert os.path.isdir(os.path.join(root_dir, 'sagify/local_test/test_dir/model'))
            assert os.path.isdir(os.path.join(root_dir, 'sagify/local_test/test_dir/output'))

    assert result.exit_code == 0


def test_init_when_directory_already_exists():
    runner = CliRunner()
    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with runner.isolated_filesystem():
            os.mkdir('sagify')

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
