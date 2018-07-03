from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    setup_cfg=True,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    packages=find_packages(where='.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    setup_requires=['setuptools>=39.1.0'],
    url='https://github.com/Kenza-AI/sagify',
    package_data={
        'sagify': [
            'template/cookiecutter.json',
            'template/{{ cookiecutter.module_slug }}/config.json',
            'template/{{ cookiecutter.module_slug }}/*.sh',
            'template/{{ cookiecutter.module_slug }}/Dockerfile',
            'template/{{ cookiecutter.module_slug }}/__init__.py',
            'template/{{ cookiecutter.module_slug }}/training/__init__.py',
            'template/{{ cookiecutter.module_slug }}/training/train',
            'template/{{ cookiecutter.module_slug }}/prediction/*.py',
            'template/{{ cookiecutter.module_slug }}/prediction/serve',
            'template/{{ cookiecutter.module_slug }}/prediction/nginx.conf',
            'template/{{ cookiecutter.module_slug }}/local_test/*.sh',
            'template/{{ cookiecutter.module_slug }}/local_test/test_dir/output/.gitkeep',
            'template/{{ cookiecutter.module_slug }}/local_test/test_dir/model/.gitkeep',
            'template/{{ cookiecutter.module_slug }}/local_test/test_dir/input/config/*.json',
            'template/{{ cookiecutter.module_slug }}/local_test/test_dir/input/data/training/'
            '.gitkeep'
        ]
    },
    install_requires=[
        'boto3==1.7.41, <1.7.99',
        'cookiecutter>=1.6.0, <1.6.99',
        'click>=6.7, <6.7.99',
        'docker==3.1.0, <3.1.99',
        'flask>=0.12.2, <0.12.99',
        'pathlib2>=2.3.0, <2.3.99',
        'sagemaker>=1.5.1, <1.5.99',
        'six>=1.10, <1.11.99'
    ],
    test_suite='tests',
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'sagify=sagify.__main__:cli',
        ],
    }
)
