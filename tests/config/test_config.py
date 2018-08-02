from sagify.config.config import ConfigManager, Config


def test_config(tmpdir):
    config_file = tmpdir.join('config.json')
    config_file.write("""
    {
        "ecr_repository_name": "ecr-repository",
        "image_name": "keras-app-img",
        "aws_profile": "sagemaker",
        "aws_region": "us-east-1"
    }
    """)
    config_manager = ConfigManager(str(config_file))
    actual_config_obj = config_manager.get_config()
    assert actual_config_obj.to_dict() == Config(
        ecr_repository_name='ecr-repository',
        image_name="keras-app-img",
        aws_profile="sagemaker",
        aws_region="us-east-1"
    ).to_dict()
