from setuptools import setup, find_packages


with open('requirements.txt', 'r') as fp:
    requirements = [x.strip() for x in fp.readlines()]

setup(
    name="llm_gateway",
    version="0.1.0",
    python_requires='~=3.11',
    packages=find_packages(),
    install_requires=requirements,
    setup_requires=['setuptools>=39.1.0'],
    url='https://github.com/Kenza-AI/sagify/llm-gateway',
    test_suite='tests'
)
