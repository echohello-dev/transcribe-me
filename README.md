Sure, here's the updated README with instructions for using Make commands for setup and running the application:

# Transcribe Me

Transcribe Me is a CLI-driven Python application that transcribes audio files using the OpenAI Whisper API and generates summaries of the transcriptions using both OpenAI's GPT-4 and Anthropic's Claude models.

## Setup

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

## Usage

1. Place your audio files in the `input` directory (or any other directory specified in the configuration).
2. Run the application:

   ```bash
   transcribe-me
   ```

   ```bash
   make transcribe
   ```

   The application will transcribe each audio file in the input directory and save the transcriptions to the output directory. It will also generate summaries of the transcriptions using the configured models and save them to the output directory.

## Additional Make Commands

- `freeze`: Saves the installed Python package versions to the `requirements.txt` file.
- `install-cli`: Installs the application as a command-line interface (CLI) tool.

## Features

- **Audio Transcription**: Transcribes audio files using the OpenAI Whisper API. It supports both MP3 and M4A formats and can handle large files by splitting them into smaller chunks for transcription.
- **Summary Generation**: Generates summaries of the transcriptions using both OpenAI's GPT-4 and Anthropic's Claude models. The summaries are saved in Markdown format and include key points in bold and a "Next Steps" section.
- **Configurable Models**: Supports multiple models for OpenAI and Anthropic, with configurable temperature, max_tokens, and system prompts.
- **Error Handling**: The application handles errors gracefully and provides informative error messages. It also cleans up temporary files after processing each audio file.

## Limitations

- The application requires API keys for both OpenAI and Anthropic. These keys are not provided with the application and must be obtained separately.
- The application is designed to run on a single machine and does not support distributed processing. As a result, the speed of transcription and summary generation is limited by the performance of the machine it is running on.
- The application does not support real-time transcription or summary generation. It processes audio files one at a time and must complete the transcription and summary generation for each file before moving on to the next one.

## Future Work

- **Parallel Processing**: Implement parallel processing to transcribe multiple audio files or chunks of audio simultaneously.
- **Real-Time Transcription and Summary Generation**: Modify the application to support real-time transcription and summary generation.
- **User Interface**: Develop a user interface to make the application more accessible to non-technical users.