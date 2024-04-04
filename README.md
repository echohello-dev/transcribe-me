# Transcribe Me

Transcribe Me is a CLI-driven Python application that transcribes audio files using the OpenAI Whisper API and generates summaries of the transcriptions using both OpenAI's GPT-4 and Anthropic's Claude-3-Sonnet models.

## Setup

1. Clone the repository.
2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Set the following environment variables:

    ```bash
    export OPENAI_API_KEY=<your_openai_api_key>
    export ANTHROPIC_API_KEY=<your_anthropic_api_key>
    ```

## Usage

1. Place your audio files in the `input` directory.
2. Run the application:

    ```bash
    python main.py
    ```

The application will transcribe each audio file in the `input` directory and save the transcriptions to the `output` directory. It will also generate summaries of the transcriptions and save them to the `output` directory.

## Features

- **Audio Transcription**: Transcribes audio files using the OpenAI Whisper API. It supports both MP3 and M4A formats and can handle large files by splitting them into smaller chunks for transcription.
- **Summary Generation**: Generates summaries of the transcriptions using both OpenAI's GPT-4 and Anthropic's Claude-3-Sonnet models. The summaries are saved in Markdown format and include key points in bold and a "Next Steps" section.
- **Error Handling**: The application handles errors gracefully and provides informative error messages. It also cleans up temporary files after processing each audio file.

## Limitations

- The application requires API keys for both OpenAI and Anthropic. These keys are not provided with the application and must be obtained separately.
- The application is designed to run on a single machine and does not support distributed processing. As a result, the speed of transcription and summary generation is limited by the performance of the machine it is running on.
- The application does not support real-time transcription or summary generation. It processes audio files one at a time and must complete the transcription and summary generation for each file before moving on to the next one.

## Future Work

- **Parallel Processing**: Implement parallel processing to transcribe multiple audio files or chunks of audio simultaneously.
- **Real-Time Transcription and Summary Generation**: Modify the application to support real-time transcription and summary generation.
- **User Interface**: Develop a user interface to make the application more accessible to non-technical users.