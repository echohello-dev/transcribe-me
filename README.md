# Transcribe Me

Transcribe Me is a CLI-driven Python application that transcribes audio files using the OpenAI Whisper API and generates summaries of the transcriptions using both OpenAI's GPT-4 and Anthropic's Claude models.

```mermaid
graph TD
    A[Load Config] --> B[Get Audio Files]
    B --> C{Audio File Exists?}
    C --Yes--> D[Transcribe Audio File]
    D --> E[Generate Summaries]
    E --> F[Save Transcription]
    F --> G[Save Summaries]
    G --> H[Clean Up Temporary Files]
    H --> B
    C --No--> I[Print Warning]
    I --> B
```

## :key: Key Features

- **Audio Transcription**: Transcribes audio files using the OpenAI Whisper API. It supports both MP3 and M4A formats and can handle large files by splitting them into smaller chunks for transcription.
- **Summary Generation**: Generates summaries of the transcriptions using both OpenAI's GPT-4 and Anthropic's Claude models. The summaries are saved in Markdown format and include key points in bold and a "Next Steps" section.
- **Configurable Models**: Supports multiple models for OpenAI and Anthropic, with configurable temperature, max_tokens, and system prompts.

## :rocket: How it Works

The Transcribe Me application follows a straightforward workflow:

1. **Load Configuration**: The application loads the configuration from the `.transcribe.yaml` file, which includes settings for input/output directories, models, and their configurations.
2. **Get Audio Files**: The application gets a list of audio files from the input directory specified in the configuration.
3. **Check Existing Transcriptions**: For each audio file, the application checks if there is an existing transcription file. If a transcription file exists, it skips to the next audio file.
4. **Transcribe Audio File**: If no transcription file exists, the application transcribes the audio file using the OpenAI Whisper API. It splits the audio file into smaller chunks for efficient transcription.
5. **Generate Summaries**: After transcription, the application generates summaries of the transcription using the configured models (OpenAI GPT-4 and Anthropic Claude).
6. **Save Transcription and Summaries**: The application saves the transcription to a text file and the summaries from each configured model to separate Markdown files in the output directory.
7. **Clean Up Temporary Files**: The application removes any temporary files generated during the transcription process.
8. **Repeat**: The process repeats for each audio file in the input directory.

## :computer: Setup

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

3. Run the `transcribe-me install` command to create the `.transcribe.yaml` configuration file and provide your API keys for OpenAI and Anthropic:

   ```bash
   make transcribe-install
   ```

4. (Optional) Install the application as a command-line interface (CLI) tool:

   ```bash
   make install-cli
   ```

## :wrench: Usage

1. Bootstrap your current directory with the configuration file:

   ```bash
   transcribe-me install
   ```

2. Place your audio files in the `input` directory (or any other directory specified in the configuration).
3. Run the application:

   ```bash
   transcribe-me
   ```

   The application will transcribe each audio file in the input directory and save the transcriptions to the output directory. It will also generate summaries of the transcriptions using the configured models and save them to the output directory.

4. (Optional) You can archive the input directory to keep track of the processed audio files:

   ```bash
   transcribe-me archive
   ```

### Docker

You can also run the application using Docker:

1. Run the following command to run the application in Docker:

    ```bash
    docker run \
        --rm \
        -v $(pwd)/input:/app/input \
        -v $(pwd)/output:/app/output \
        -v $(pwd)/.transcribe.yaml:/app/.transcribe.yaml \
        ghcr.io/echohello-dev/transcribe-me:latest
    ```

    This command mounts the `input` and `output` directories and the `.transcribe.yaml` configuration file into the Docker container.

2. (Optional) We can also run the application using the provided `docker-compose.yml` file:

    ```yaml
    version: '3'
    services:
      transcribe-me:
        image: ghcr.io/echohello-dev/transcribe-me:latest
        volumes:
          - ./input:/app/input
          - ./output:/app/output
          - ./archive:/app/archive
          - ./.transcribe.yaml:/app/.transcribe.yaml
    ```

   Run the following command to start the application using Docker Compose:

   ```bash
   docker compose run --rm app
   ```

   This command mounts the `input`, `output`, `archive`, and `.transcribe.yaml` configuration file into the Docker container. See [`compose.example.yaml`](./compose.example.yaml) for an example configuration.

## :gear: Configuration

The application uses a configuration file (`.transcribe.yaml`) to specify settings such as input/output directories, API keys, models, and their configurations. The configuration file is created automatically when you run the `transcribe-me install` command.

> `max_tokens` is the maximum number of tokens to generate in the summary. The default is dynamic based on the model.

Here is an example configuration file:

```yaml
openai:
  models:
    - temperature: 0.1
      max_tokens: 2048
      model: gpt-4
      system_prompt: Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.

anthropic:
  models:
    - temperature: 0.8
      model: claude-3-sonnet-20240229
      system_prompt: Generate something creative and interesting, use Markdown, be a concise tech expert but kind to non-technical readers.

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