# Transcribe Me

[![Release](https://github.com/echohello-dev/transcribe-me/actions/workflows/release.yaml/badge.svg?branch=main)](https://github.com/echohello-dev/transcribe-me/actions/workflows/release.yaml)

[![Build](https://github.com/echohello-dev/transcribe-me/actions/workflows/build.yaml/badge.svg)](https://github.com/echohello-dev/transcribe-me/actions/workflows/build.yaml)

Transcribe Me is a CLI-driven Python application that transcribes audio files using either the OpenAI Whisper API or AssemblyAI.

```mermaid
graph TD
    A[Load Config] --> B[Get Audio Files]
    B --> C{Audio File Exists?}
    C --Yes--> D{Use AssemblyAI?}
    D --Yes--> E[Transcribe with AssemblyAI]
    D --No--> F[Transcribe with OpenAI]
    E --> G[Generate Additional Outputs]
    F --> I[Save Transcription]
    G --> I
    I --> K[Clean Up Temporary Files]
    K --> B
    C --No--> L[Print Warning]
    L --> B
```

## :key: Key Features

- **Audio Transcription**: Transcribes audio files using either the OpenAI Whisper API or AssemblyAI. It supports both MP3 and M4A formats.
- **AssemblyAI Features**: When using AssemblyAI, provides additional outputs including Speaker Diarization, Summary, Sentiment Analysis, Key Phrases, and Topic Detection.
- **Supports Audio Files**: Supports audio files in `.m4a` and `.mp3` formats.
- **Supports Docker**: Can be run in a Docker container for easy deployment and reproducibility.

## :package: Installation

Tool has been tested with Python 3.12.

### macOS

This has been tested with macOS, your mileage may vary on other operating systems like Windows, WSL or Linux.

1. Install Python. Recommended way is to use [asdf](https://asdf-vm.com/guide/getting-started.html):

    ```bash
    brew install asdf
    asdf plugin add python
    asdf install python 3.12.0
    asdf global python 3.12.0
    ```

2. Install FFmpeg using Homebrew:

   ```bash
   brew install ffmpeg
   ```

3. Install the application using pip:

    ```
    pip install transcribe-me
    ```

## :wrench: Usage

1. Bootstrap your current directory with the configuration file:

    ```bash
    transcribe-me install
    ```

    This command will prompt you to enter your API keys for OpenAI and AssemblyAI if they are not already provided in environment variables. You can also set the API keys in environment variables:

    ```bash
    export OPENAI_API_KEY=your_api_key
    export ASSEMBLYAI_API_KEY=your_api_key
    ```

2. Place your audio files in the `input` directory (or any other directory specified in the configuration).
3. Run the application:

   ```bash
   transcribe-me
   ```

   The application will transcribe each audio file in the input directory and save the transcriptions to the output directory.

4. (Optional) You can archive the input directory to keep track of the processed audio files:

   ```bash
   transcribe-me archive
   ```

### Docker

You can also run the application using Docker:

1. Install Docker on your machine by following the instructions on the [Docker website](https://docs.docker.com/get-docker/).

2. Create a `.transcribe.yaml` configuration file:

    ```bash
    touch .transcribe.yaml
    docker run \
        --rm \
        -v $(pwd)/.transcribe.yaml:/app/.transcribe.yaml \
        ghcr.io/echohello-dev/transcribe-me:latest install
    ```

3. Run the following command to run the application in Docker:

    ```bash
    docker run \
        --rm \
        -e OPENAI_API_KEY \
        -e ASSEMBLYAI_API_KEY \
        -v $(pwd)/archive:/app/archive \
        -v $(pwd)/input:/app/input \
        -v $(pwd)/output:/app/output \
        -v $(pwd)/.transcribe.yaml:/app/.transcribe.yaml \
        ghcr.io/echohello-dev/transcribe-me:latest
    ```

    This command mounts the `input` and `output` directories and the `.transcribe.yaml` configuration file into the Docker container.

4. (Optional) We can also run the application using the provided `docker-compose.yml` file:

    ```yaml
    version: '3'
    services:
      transcribe-me:
        image: ghcr.io/echohello-dev/transcribe-me:latest
        environment:
          - OPENAI_API_KEY
          - ASSEMBLYAI_API_KEY
        volumes:
          - ./input:/app/input
          - ./output:/app/output
          - ./archive:/app/archive
          - ./.transcribe.yaml:/app/.transcribe.yaml
    ```

    Run the following command to start the application using Docker Compose:

    ```bash
    docker compose run --rm transcribe-me
    ```

    This command mounts the `input`, `output`, `archive`, and `.transcribe.yaml` configuration file into the Docker container. See [`compose.example.yaml`](./compose.example.yaml) for an example configuration.

    Make sure to replace `OPENAI_API_KEY` and `ASSEMBLYAI_API_KEY` with your actual API keys. Also make sure to create the `.transcribe.yaml` configuration file in the same directory as the `docker-compose.yml` file.

## :rocket: How it Works

The Transcribe Me application follows a straightforward workflow:

1. **Load Configuration**: The application loads the configuration from the `.transcribe.yaml` file, which includes settings for input/output directories and transcription service.
2. **Get Audio Files**: The application gets a list of audio files from the input directory specified in the configuration.
3. **Check Existing Transcriptions**: For each audio file, the application checks if there is an existing transcription file. If a transcription file exists, it skips to the next audio file.
4. **Transcribe Audio File**: If no transcription file exists, the application transcribes the audio file using either the OpenAI Whisper API or AssemblyAI, based on the configuration.
5. **Generate Outputs**:
   - For OpenAI: The application generates summaries of the transcription using the configured models (OpenAI GPT-4 and Anthropic Claude).
   - For AssemblyAI: The application generates additional outputs including Speaker Diarization, Summary, Sentiment Analysis, Key Phrases, and Topic Detection.
6. **Save Transcription and Outputs**: The application saves the transcription and all generated outputs to separate files in the output directory.
7. **Clean Up Temporary Files**: The application removes any temporary files generated during the transcription process.
8. **Repeat**: The process repeats for each audio file in the input directory.

## :gear: Configuration

The application uses a configuration file (`.transcribe.yaml`) to specify settings such as input/output directories, API keys, models, and their configurations. The configuration file is created automatically when you run the `transcribe-me install` command.

Here is an example configuration file:

```yaml
use_assemblyai: false  # Set to true to use AssemblyAI instead of OpenAI for transcription

input_folder: input
output_folder: output
```

## Additional Make Commands

- `freeze`: Saves the installed Python package versions to the `requirements.txt` file.
- `install-cli`: Installs the application as a command-line interface (CLI) tool.

## Limitations

- The application requires API keys for both OpenAI and Anthropic. These keys are not provided with the application and must be obtained separately.
- The application is designed to run on a single machine and does not support distributed processing. As a result, the speed of transcription and summary generation is limited by the performance of the machine it is running on.
- The application does not support real-time transcription or summary generation. It processes audio files one at a time and must complete the transcription and summary generation for each file before moving on to the next one.

## :writing_hand: Contibuting

1. Clone the repository.
2. Install the required tools using ASDF (for managing tool versions) and Homebrew (for installing dependencies):

   - Install ASDF:

   ```bash
   brew install asdf
   ```

   - Install FFmpeg using Homebrew:

   ```bash
   brew install ffmpeg
   ```

3. Install the Python dependencies and create a virtual environment:

   ```bash
   make install
   ```

3. Run the `transcribe-me install` command to create the `.transcribe.yaml` configuration file and provide your API keys for OpenAI and AssemblyAI:

   ```bash
   make transcribe-install
   ```

4. (Optional) Install the application as a command-line interface (CLI) tool:

   ```bash
   make install-cli
   ```

### Workflows

This project uses several GitHub Actions workflows to automate various processes:

- **Build**: Triggered on pushes and pull requests to the `main` branch. It installs dependencies, runs linting, tests, and builds the project.

- **Fix Release**: Manually triggered workflow that allows fixing a specific version release. It publishes the package, Docker image, and updates the release.

- **Publish Latest Image**: Triggered on pushes to the `main` branch. It publishes the latest Docker image for multiple architectures.

- **Pull Request Release**: Triggered when a pull request is opened, reopened, or synchronized. It uses Release Drafter to draft a release based on the pull request.

- **Release**: Triggered on pushes to the `main` branch. It drafts a new release using Release Drafter, publishes the package and Docker image, and publishes the drafted release.

### Releasing a New Version

This project uses [Release Drafter](https://github.com/release-drafter/release-drafter) to automatically generate release notes and determine the version number based on the labels of merged pull requests.

To release a new version:

1. Ensure that your pull request has one of the following labels:
   - `major`: For a major version bump (e.g., 1.0.0 -> 2.0.0)
   - `minor`: For a minor version bump (e.g., 1.0.0 -> 1.1.0)
   - `patch`: For a patch version bump (e.g., 1.0.0 -> 1.0.1)

   If no label is provided, the default behavior is to bump the patch version.

2. Merge the pull request into the `main` branch.

3. The "Release" workflow will automatically trigger and perform the following steps:
   - Draft a new release using Release Drafter, determining the version number based on the merged pull request labels.
   - Publish the package to PyPI.
   - Publish the Docker image for multiple architectures.
   - Publish the drafted release on GitHub.

4. If there are any issues with the release, you can manually trigger the "Fix Release" workflow and provide the version number to fix the release.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=echohello-dev/transcribe-me&type=Date)](https://star-history.com/#echohello-dev/transcribe-me&Date)
