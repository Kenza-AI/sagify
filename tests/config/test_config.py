from sagify.config.config import ConfigManager, Config


def test_config(tmpdir):
    config_file = tmpdir.join('config.json')
    config_file.write("""
    {
        "image_name": "keras-app-img",
        "aws_profile": "sagemaker",
        "aws_region": "us-east-1",
        "python_version": "3.6",
        "sagify_module_dir": "keras-app-img",
        "requirements_dir": "requirements.txt"
    }
    """)
    config_manager = ConfigManager(str(config_file))
    actual_config_obj = config_manager.get_config()
    assert actual_config_obj.to_dict() == Config(
        image_name="keras-app-img", aws_profile="sagemaker", aws_region="us-east-1", python_version="3.6", sagify_module_dir="keras-app-img",
        requirements_dir="requirements.txt"
    ).to_dict()
