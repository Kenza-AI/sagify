from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='sagify',
    version='0.20.8',
    setup_cfg=True,
    python_requires='~=3.5',
    packages=find_packages(where='.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    setup_requires=['setuptools>=39.1.0'],
    url='https://github.com/Kenza-AI/sagify',
    package_data={
        'sagify': [
            'template/sagify_base/config.json',
            'template/sagify_base/*.sh',
            'template/sagify_base/Dockerfile',
            'template/sagify_base/__init__.py',
            'template/sagify_base/training/__init__.py',
            'template/sagify_base/training/train',
            'template/sagify_base/training/*.py',
            'template/sagify_base/prediction/*.py',
            'template/sagify_base/prediction/serve',
            'template/sagify_base/prediction/nginx.conf',
            'template/sagify_base/local_test/*.sh',
            'template/sagify_base/local_test/test_dir/output/.gitkeep',
            'template/sagify_base/local_test/test_dir/model/.gitkeep',
            'template/sagify_base/local_test/test_dir/input/config/*.json',
            'template/sagify_base/local_test/test_dir/input/data/training/'
            '.gitkeep'
        ]
    },
    install_requires=[
        'boto3',
        'click>=7.0, <7.0.99',
        'docker>=3.7.0, <3.7.99',
        'flask>=1.1.0, <1.1.99',
        'paramiko>=2.4.2, <2.4.99',
        'pathlib2>=2.3.0, <2.3.99',
        'requests>=2.20.0, <2.20.99',
        'sagemaker>=1.50.0, <1.50.99',
        'six>=1.10, <1.11.99',
        'future>=0.16.0, <0.17.99'
    ],
    test_suite='tests',
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'sagify=sagify.__main__:cli',
        ],
    }
)
