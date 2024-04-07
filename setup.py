from setuptools import setup, find_packages

setup(
    name='transcribe_me',
    description='A CLI tool to transcribe audio files using OpenAI API',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'transcribe-me = transcribe_me.main:main',
        ],
    },
    install_requires=[
        'openai',
        'anthropic',
        'pydub',
    ],
)