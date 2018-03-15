import os
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from sagify.main import cli


def test_init_happy_case():
    runner = CliRunner()
    
    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with runner.isolated_filesystem():
            result = runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\nus-east-1\n')

            assert os.path.isdir('sagify')
            assert os.path.isdir('sagify/training')
            assert os.path.isdir('sagify/prediction')
            assert os.path.isfile('sagify/__init__.py')
            assert os.path.isfile('sagify/build_and_push.sh')
            assert os.path.isfile('sagify/Dockerfile')
            assert os.path.isfile('sagify/training/__init__.py')
            assert os.path.isfile('sagify/training/train')
            assert os.path.isfile('sagify/prediction/__init__.py')
            assert os.path.isfile('sagify/prediction/nginx.conf')
            assert os.path.isfile('sagify/prediction/predictor.py')
            assert os.path.isfile('sagify/prediction/wsgi.py')
            assert os.path.isfile('sagify/prediction/serve')

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

            assert os.path.isdir(os.path.join(root_dir, 'sagify'))
            assert os.path.isdir(os.path.join(root_dir, 'sagify/training'))
            assert os.path.isdir(os.path.join(root_dir, 'sagify/prediction'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/__init__.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/build_and_push.sh'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/Dockerfile'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/training/__init__.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/training/train'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/__init__.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/nginx.conf'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/predictor.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/wsgi.py'))
            assert os.path.isfile(os.path.join(root_dir, 'sagify/prediction/serve'))

    assert result.exit_code == 0


def test_init_when_directory_already_exists_and_user_does_not_overwrite_it():
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

            assert os.path.isdir('my_sagify')
            assert os.path.isdir('my_sagify/training')
            assert os.path.isdir('my_sagify/prediction')
            assert os.path.isfile('my_sagify/__init__.py')
            assert os.path.isfile('my_sagify/build_and_push.sh')
            assert os.path.isfile('my_sagify/Dockerfile')
            assert os.path.isfile('my_sagify/training/__init__.py')
            assert os.path.isfile('my_sagify/training/train')
            assert os.path.isfile('my_sagify/prediction/__init__.py')
            assert os.path.isfile('my_sagify/prediction/nginx.conf')
            assert os.path.isfile('my_sagify/prediction/predictor.py')
            assert os.path.isfile('my_sagify/prediction/wsgi.py')
            assert os.path.isfile('my_sagify/prediction/serve')

    assert result.exit_code == 0


def test_init_when_directory_already_exists_and_user_does_overwrite_it():
    runner = CliRunner()
    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=['default', 'sagemaker']
    ):
        with runner.isolated_filesystem():
            os.mkdir('sagify')
            os.mkdir('sagify/my_module')

            result = runner.invoke(
                cli=cli,
                args=['init'],
                input='my_app\n1\n2\nus-east-1\nY\n'
            )

            assert os.path.isdir('sagify')
            assert os.path.isdir('sagify/training')
            assert os.path.isdir('sagify/prediction')
            assert os.path.isfile('sagify/__init__.py')
            assert os.path.isfile('sagify/build_and_push.sh')
            assert os.path.isfile('sagify/Dockerfile')
            assert os.path.isfile('sagify/training/__init__.py')
            assert os.path.isfile('sagify/training/train')
            assert os.path.isfile('sagify/prediction/__init__.py')
            assert os.path.isfile('sagify/prediction/nginx.conf')
            assert os.path.isfile('sagify/prediction/predictor.py')
            assert os.path.isfile('sagify/prediction/wsgi.py')
            assert os.path.isfile('sagify/prediction/serve')

    assert result.exit_code == 0


def test_init_when_aws_cli_is_not_configure_locally():
    runner = CliRunner()
    with patch(
            'sagify.commands.initialize._get_local_aws_profiles',
            return_value=[]
    ):
        with runner.isolated_filesystem():
            result = runner.invoke(cli=cli, args=['init'], input='my_app\n1\n2\n')

    assert result.exit_code == -1
