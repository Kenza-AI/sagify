from setuptools import find_packages, setup

setup(
    setup_cfg=True,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    packages=find_packages(where='.'),
    install_requires=[
        'boto3==1.6.3, <1.6.99',
        'cookiecutter>=1.6.0, <1.6.99',
        'click>=6.7, <6.7.99',
        'docker==3.1.0, <3.1.99',
        'flask>=0.12.2, <0.12.99',
        'sagemaker>=1.1.3, <1.1.99',
        'six>=1.10, <1.11.99'
    ],
    test_suite='tests',
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'sagify=sagify.main:cli',
        ],
    }
)
