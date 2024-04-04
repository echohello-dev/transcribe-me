from setuptools import setup, find_packages

setup(
    name='transcribe_me',
    description='A tool for transcribing audio files using the OpenAI Whisper API.',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'transcribe-me = transcribe_me.main:main',
        ],
    },
    install_requires=[
        # List your project's dependencies here
        'openai',
        'anthropic',
        'pydub',
        'tqdm',
        # ...
    ],
)