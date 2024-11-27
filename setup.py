from setuptools import setup, find_packages

setup(
    name='lmsystems',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
        'langgraph>=0.2.53',
        'langgraph_sdk>=0.1.36',
        'pyjwt>=2.0.0',
        'cryptography>=3.4.8',
    ],
    author='Sean Sullivan',
    author_email='sean.sullivan3@yahoo.com',
    description='SDK for integrating purchased graphs from the lmsystems marketplace.',
    url='https://github.com/RVCA212/lmsystems-sdk',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
