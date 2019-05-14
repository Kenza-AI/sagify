from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='sagify',
    version='0.17.0',
    setup_cfg=True,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    packages=find_packages(where='.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    setup_requires=['setuptools>=39.1.0'],
    url='https://github.com/Kenza-AI/sagify',
    package_data={
        'sagify': [
            'template/sagify/config.json',
            'template/sagify/*.sh',
            'template/sagify/Dockerfile',
            'template/sagify/__init__.py',
            'template/sagify/training/__init__.py',
            'template/sagify/training/train',
            'template/sagify/prediction/*.py',
            'template/sagify/prediction/serve',
            'template/sagify/prediction/nginx.conf',
            'template/sagify/local_test/*.sh',
            'template/sagify/local_test/test_dir/output/.gitkeep',
            'template/sagify/local_test/test_dir/model/.gitkeep',
            'template/sagify/local_test/test_dir/input/config/*.json',
            'template/sagify/local_test/test_dir/input/data/training/'
            '.gitkeep'
        ]
    },
    install_requires=[
        'boto3==1.9.64, <1.9.99',
        'click>=6.7, <6.7.99',
        'docker>=3.7.0, <3.7.99',
        'flask>=0.12.2, <0.12.99',
        'paramiko>=2.4.2, <2.4.99',
        'pathlib2>=2.3.0, <2.3.99',
        'requests>=2.20.0, <2.20.99',
        'sagemaker>=1.17.0, <1.17.99',
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
