from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='sagify',
    version='0.24.0',
    setup_cfg=True,
    python_requires='~=3.7',
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
        'click>=8.1.0, <8.1.99',
        'docker>=7.0.0, <7.0.99',
        'fastapi>=0.109.0, <0.109.99',
        'future>=0.18.0, <0.18.99',
        'pydantic>=2.6.0, <2.6.99',
        'python-dotenv>=1.0.0, <1.0.99',
        'sagemaker>=2.202.0, <2.202.99',
        'six>=1.16, <1.16.99',
        'structlog>=24.1.0, <24.1.99',
        'uvicorn>=0.27.0, <0.27.99',
    ],
    test_suite='tests',
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'sagify=sagify.__main__:cli',
        ],
    }
)
