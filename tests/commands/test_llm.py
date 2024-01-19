# -*- coding: utf-8 -*-
import json
import os
try:
    from unittest.mock import patch, call
except ImportError:
    from mock import patch, call

from click.testing import CliRunner
from sagify.__main__ import cli


class TestLlmStart(object):
    def test_start_all_happy_case(self):
        runner = CliRunner()
        with patch(
            'sagify.api.cloud.foundation_model_deploy'
        ) as mocked_foundation_model_deploy:
            mocked_foundation_model_deploy.side_effect = [
                ('chat_completions_endpoint', 'some code snippet 1'),
                ('image_creations_endpoint', 'some code snippet 2'),
                ('embeddings_endpoint', 'some code snippet 3'),
            ]
            with runner.isolated_filesystem():
                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'start',
                        '--all',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production'
                    ]
                )

                assert mocked_foundation_model_deploy.call_count == 3
                mocked_foundation_model_deploy.assert_has_calls(
                    [
                        call(
                            model_id='meta-textgeneration-llama-2-7b-f',
                            model_version='1.*',
                            num_instances=1,
                            ec2_type='ml.g5.2xlarge',
                            aws_region='us-east-1',
                            aws_profile='sagemaker-production',
                            aws_role=None,
                            external_id=None,
                            tags=None
                        ),
                        call(
                            model_id='model-txt2img-stabilityai-stable-diffusion-v2-1-base',
                            model_version='1.*',
                            num_instances=1,
                            ec2_type='ml.p3.2xlarge',
                            aws_region='us-east-1',
                            aws_profile='sagemaker-production',
                            aws_role=None,
                            external_id=None,
                            tags=None
                        ),
                        call(
                            model_id='huggingface-sentencesimilarity-gte-small',
                            model_version='1.*',
                            num_instances=1,
                            ec2_type='ml.g5.2xlarge',
                            aws_region='us-east-1',
                            aws_profile='sagemaker-production',
                            aws_role=None,
                            external_id=None,
                            tags=None
                        )
                    ]
                )

                assert os.path.isfile('.sagify_llm_infra.json')

                with open('.sagify_llm_infra.json', 'r') as f:
                    llm_infra_config = json.load(f)

                assert llm_infra_config['chat_completions_endpoint'] is not None
                assert llm_infra_config['image_creations_endpoint'] is not None
                assert llm_infra_config['embeddings_endpoint'] is not None

                assert result.exit_code == 0

    def test_start_chat_completions_only(self):
        runner = CliRunner()
        with patch(
            'sagify.api.cloud.foundation_model_deploy'
        ) as mocked_foundation_model_deploy:
            mocked_foundation_model_deploy.side_effect = [
                ('chat_completions_endpoint', 'some code snippet 1')
            ]
            with runner.isolated_filesystem():
                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'start',
                        '--chat-completions',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production'
                    ]
                )

                assert mocked_foundation_model_deploy.call_count == 1
                mocked_foundation_model_deploy.assert_called_with(
                    model_id='meta-textgeneration-llama-2-7b-f',
                    model_version='1.*',
                    num_instances=1,
                    ec2_type='ml.g5.2xlarge',
                    aws_region='us-east-1',
                    aws_profile='sagemaker-production',
                    aws_role=None,
                    external_id=None,
                    tags=None
                )

                assert os.path.isfile('.sagify_llm_infra.json')

                with open('.sagify_llm_infra.json', 'r') as f:
                    llm_infra_config = json.load(f)

                assert llm_infra_config['chat_completions_endpoint'] is not None
                assert llm_infra_config['image_creations_endpoint'] is None
                assert llm_infra_config['embeddings_endpoint'] is None

                assert result.exit_code == 0

    def test_start_image_creations_only(self):
        runner = CliRunner()
        with patch(
            'sagify.api.cloud.foundation_model_deploy'
        ) as mocked_foundation_model_deploy:
            mocked_foundation_model_deploy.side_effect = [
                ('image_creations_endpoint', 'some code snippet 2')
            ]
            with runner.isolated_filesystem():
                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'start',
                        '--image-creations',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production'
                    ]
                )

                assert mocked_foundation_model_deploy.call_count == 1
                mocked_foundation_model_deploy.assert_called_with(
                    model_id='model-txt2img-stabilityai-stable-diffusion-v2-1-base',
                    model_version='1.*',
                    num_instances=1,
                    ec2_type='ml.p3.2xlarge',
                    aws_region='us-east-1',
                    aws_profile='sagemaker-production',
                    aws_role=None,
                    external_id=None,
                    tags=None
                )

                assert os.path.isfile('.sagify_llm_infra.json')

                with open('.sagify_llm_infra.json', 'r') as f:
                    llm_infra_config = json.load(f)

                assert llm_infra_config['chat_completions_endpoint'] is None
                assert llm_infra_config['image_creations_endpoint'] is not None
                assert llm_infra_config['embeddings_endpoint'] is None

                assert result.exit_code == 0

    def test_start_embeddings_only(self):
        runner = CliRunner()
        with patch(
            'sagify.api.cloud.foundation_model_deploy'
        ) as mocked_foundation_model_deploy:
            mocked_foundation_model_deploy.side_effect = [
                ('embeddings_endpoint', 'some code snippet 3')
            ]
            with runner.isolated_filesystem():
                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'start',
                        '--embeddings',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production'
                    ]
                )

                assert mocked_foundation_model_deploy.call_count == 1
                mocked_foundation_model_deploy.assert_called_with(
                    model_id='huggingface-sentencesimilarity-gte-small',
                    model_version='1.*',
                    num_instances=1,
                    ec2_type='ml.g5.2xlarge',
                    aws_region='us-east-1',
                    aws_profile='sagemaker-production',
                    aws_role=None,
                    external_id=None,
                    tags=None
                )

                assert os.path.isfile('.sagify_llm_infra.json')

                with open('.sagify_llm_infra.json', 'r') as f:
                    llm_infra_config = json.load(f)

                assert llm_infra_config['chat_completions_endpoint'] is None
                assert llm_infra_config['image_creations_endpoint'] is None
                assert llm_infra_config['embeddings_endpoint'] is not None

                assert result.exit_code == 0


class TestLlmStop(object):
    def test_stop_all_happy_case(self):
        runner = CliRunner()
        with patch(
            'sagify.commands.llm.sagemaker.SageMakerClient'
        ) as mocked_sagemaker_client:
            with runner.isolated_filesystem():
                with open('.sagify_llm_infra.json', 'w') as f:
                    json.dump({
                        'chat_completions_endpoint': 'endpoint1',
                        'image_creations_endpoint': 'endpoint2',
                        'embeddings_endpoint': 'endpoint3'
                    }, f)

                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'stop',
                        '--all',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production',
                        '--iam-role-arn', 'arn:aws:iam::123456789012:role/MyRole',
                        '--external-id', '123456'
                    ]
                )

                mocked_sagemaker_client.assert_called_with(
                    'sagemaker-production', 'us-east-1', 'arn:aws:iam::123456789012:role/MyRole', '123456'
                )
                assert mocked_sagemaker_client.return_value.shutdown_endpoint.call_count == 3
                mocked_sagemaker_client.return_value.shutdown_endpoint.assert_has_calls(
                    [
                        call('endpoint1'),
                        call('endpoint2'),
                        call('endpoint3')
                    ]
                )

                assert result.exit_code == 0

    def test_stop_chat_completions_only(self):
        runner = CliRunner()
        with patch(
            'sagify.commands.llm.sagemaker.SageMakerClient'
        ) as mocked_sagemaker_client:
            with runner.isolated_filesystem():
                with open('.sagify_llm_infra.json', 'w') as f:
                    json.dump({
                        'chat_completions_endpoint': 'endpoint1',
                        'image_creations_endpoint': 'endpoint2',
                        'embeddings_endpoint': 'endpoint3'
                    }, f)

                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'stop',
                        '--chat-completions',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production',
                        '--iam-role-arn', 'arn:aws:iam::123456789012:role/MyRole',
                        '--external-id', '123456'
                    ]
                )

                mocked_sagemaker_client.assert_called_with(
                    'sagemaker-production', 'us-east-1', 'arn:aws:iam::123456789012:role/MyRole', '123456'
                )
                assert mocked_sagemaker_client.return_value.shutdown_endpoint.call_count == 1
                mocked_sagemaker_client.return_value.shutdown_endpoint.assert_called_with(
                    'endpoint1'
                )

                assert result.exit_code == 0

    def test_stop_image_creations_only(self):
        runner = CliRunner()
        with patch(
            'sagify.commands.llm.sagemaker.SageMakerClient'
        ) as mocked_sagemaker_client:
            with runner.isolated_filesystem():
                with open('.sagify_llm_infra.json', 'w') as f:
                    json.dump({
                        'chat_completions_endpoint': 'endpoint1',
                        'image_creations_endpoint': 'endpoint2',
                        'embeddings_endpoint': 'endpoint3'
                    }, f)

                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'stop',
                        '--image-creations',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production',
                        '--iam-role-arn', 'arn:aws:iam::123456789012:role/MyRole',
                        '--external-id', '123456'
                    ]
                )

                mocked_sagemaker_client.assert_called_with(
                    'sagemaker-production', 'us-east-1', 'arn:aws:iam::123456789012:role/MyRole', '123456'
                )
                assert mocked_sagemaker_client.return_value.shutdown_endpoint.call_count == 1
                mocked_sagemaker_client.return_value.shutdown_endpoint.assert_called_with(
                    'endpoint2'
                )

                assert result.exit_code == 0

    def test_stop_embeddings_only(self):
        runner = CliRunner()
        with patch(
            'sagify.commands.llm.sagemaker.SageMakerClient'
        ) as mocked_sagemaker_client:
            with runner.isolated_filesystem():
                with open('.sagify_llm_infra.json', 'w') as f:
                    json.dump({
                        'chat_completions_endpoint': 'endpoint1',
                        'image_creations_endpoint': 'endpoint2',
                        'embeddings_endpoint': 'endpoint3'
                    }, f)

                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'stop',
                        '--embeddings',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production',
                        '--iam-role-arn', 'arn:aws:iam::123456789012:role/MyRole',
                        '--external-id', '123456'
                    ]
                )

                mocked_sagemaker_client.assert_called_with(
                    'sagemaker-production', 'us-east-1', 'arn:aws:iam::123456789012:role/MyRole', '123456'
                )
                assert mocked_sagemaker_client.return_value.shutdown_endpoint.call_count == 1
                mocked_sagemaker_client.return_value.shutdown_endpoint.assert_called_with(
                    'endpoint3'
                )

                assert result.exit_code == 0

    def test_stop_missing_config_file(self):
        runner = CliRunner()
        with patch(
            'sagify.commands.llm.sagemaker.SageMakerClient'
        ) as mocked_sagemaker_client:
            with runner.isolated_filesystem():
                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'stop',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production',
                        '--iam-role-arn', 'arn:aws:iam::123456789012:role/MyRole',
                        '--external-id', '123456'
                    ]
                )

                assert mocked_sagemaker_client.return_value.shutdown_endpoint.call_count == 0
                assert result.exit_code == -1

    def test_stop_endpoint_shutdown_error(self):
        runner = CliRunner()
        with patch(
            'sagify.commands.llm.sagemaker.SageMakerClient'
        ) as mocked_sagemaker_client:
            mocked_sagemaker_client.return_value.shutdown_endpoint.side_effect = Exception('Endpoint shutdown error')
            with runner.isolated_filesystem():
                with open('.sagify_llm_infra.json', 'w') as f:
                    json.dump({
                        'chat_completions_endpoint': 'endpoint1',
                        'image_creations_endpoint': 'endpoint2',
                        'embeddings_endpoint': 'endpoint3'
                    }, f)

                result = runner.invoke(
                    cli=cli,
                    args=[
                        'llm', 'stop',
                        '--all',
                        '--aws-region', 'us-east-1',
                        '--aws-profile', 'sagemaker-production',
                        '--iam-role-arn', 'arn:aws:iam::123456789012:role/MyRole',
                        '--external-id', '123456'
                    ]
                )

                assert mocked_sagemaker_client.return_value.shutdown_endpoint.call_count == 1
                mocked_sagemaker_client.return_value.shutdown_endpoint.assert_called_with('endpoint1')

                assert result.exit_code == -1
