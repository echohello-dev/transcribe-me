import argparse
import os
from glob import glob
from typing import Dict, Any

import anthropic
import openai
from pydub import AudioSegment
from tqdm import tqdm
import yaml

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DEFAULT_OUTPUT_FOLDER = "output"
DEFAULT_INPUT_FOLDER = "input"
DEFAULT_CONFIG_FILE = ".transcribe.yaml"


def split_audio(file_path: str, interval_minutes: int = 10) -> list[str]:
    """
    Split an audio file into chunks of a specified length.

    Args:
        file_path (str): Path to the audio file to split.
        interval_minutes (int): Length of each chunk in minutes.

    Returns:
        list[str]: List of file paths for the generated chunks.
    """
    extension = os.path.splitext(file_path)[1]
    if extension == ".m4a":
        audio = AudioSegment.from_file(file_path, format="m4a")
    else:
        audio = AudioSegment.from_mp3(file_path)

    interval_ms = interval_minutes * 60 * 1000
    chunks = [audio[i: i + interval_ms] for i in range(0, len(audio), interval_ms)]

    chunk_names = []
    for i, chunk in enumerate(tqdm(chunks, desc="Splitting audio", unit="chunk"), start=1):
        chunk_name = f"{os.path.splitext(file_path)[0]}_part{i}.mp3"
        chunk.export(chunk_name, format="mp3")
        chunk_names.append(chunk_name)

    return chunk_names


def transcribe_chunk(file_path: str) -> str:
    """
    Transcribe an audio chunk using the OpenAI Whisper API.

    Args:
        file_path (str): Path to the audio chunk to transcribe.

    Returns:
        str: Transcribed text.
    """
    with open(file_path, "rb") as audio_file:
        try:
            response = openai.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return response.text
        except Exception as e:
            print(f"An error occurred while transcribing {file_path}: {e}")
            raise e


def transcribe_audio(file_path: str, output_path: str) -> None:
    """
    Transcribe an audio file using the OpenAI Whisper API.

    Args:
        file_path (str): Path to the audio file to transcribe.
        output_path (str): Path to the output file for the transcription.
    """
    chunk_files = split_audio(file_path)
    full_transcription = ""

    for chunk_file in tqdm(chunk_files, desc="Transcribing", unit="chunk"):
        try:
            transcription = transcribe_chunk(chunk_file)
            full_transcription += transcription + " "
        except Exception as e:
            print(f"An error occurred while transcribing chunk {chunk_file}: {e}")
        finally:
            os.remove(chunk_file)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(full_transcription)


def generate_summary(transcription: str, model_config: Dict[str, Any]) -> str:
    """
    Generate a summary from the transcription using the specified model configuration.

    Args:
        transcription (str): The full transcription text.
        model_config (Dict[str, Any]): The configuration for the model to be used for summary generation.

    Returns:
        str: The generated summary.
    """
    temperature = model_config["temperature"]
    max_tokens = model_config["max_tokens"]
    model_name = model_config["model"]
    system_prompt = model_config["system_prompt"]

    input_tokens = len(transcription.split())
    max_tokens = min(max_tokens, 3000)

    if "openai" in model_name:
        openai_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": transcription},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        summary = openai_response.choices[0].message.content.strip()
    else:
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        anthropic_response = anthropic_client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": transcription}],
        )
        summary = anthropic_response.content[0].text

    return summary


def install_config():
    """
    Create a config file in the current directory and prompt the user to input API keys if not set.
    """
    config = {
        "openai": {
            "models": [
                {
                    "temperature": 0.1,
                    "max_tokens": 2048,
                    "model": "gpt-4",
                    "system_prompt": "Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.",
                },
                {
                    "temperature": 0.3,
                    "max_tokens": 2048,
                    "model": "gpt-4",
                    "system_prompt": "Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.",
                },
                {
                    "temperature": 0.5,
                    "max_tokens": 2048,
                    "model": "gpt-4",
                    "system_prompt": "Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.",
                },
            ]
        },
        "anthropic": {
            "models": [
                {
                    "temperature": 0.1,
                    "max_tokens": 2048,
                    "model": "claude-3-sonnet-20240229",
                    "system_prompt": "Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.",
                },
                {
                    "temperature": 0.3,
                    "max_tokens": 2048,
                    "model": "claude-3-sonnet-20240229",
                    "system_prompt": "Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.",
                },
                {
                    "temperature": 0.5,
                    "max_tokens": 2048,
                    "model": "claude-3-sonnet-20240229",
                    "system_prompt": "Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.",
                },
            ]
        },
        "input_folder": DEFAULT_INPUT_FOLDER,
        "output_folder": DEFAULT_OUTPUT_FOLDER,
    }

    if not OPENAI_API_KEY:
        print("Looks like you haven't set your OpenAI API key. We'll set it up for you.")
        openai_key = input("Enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = openai_key
        append_to_shell_profile(f"export OPENAI_API_KEY={openai_key}")

    if not ANTHROPIC_API_KEY:
        print("Looks like you haven't set your Anthropic API key. We'll set it up for you.")
        anthropic_key = input("Enter your Anthropic API key: ")
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        append_to_shell_profile(f"export ANTHROPIC_API_KEY={anthropic_key}")

    with open(DEFAULT_CONFIG_FILE, "w") as f:
        yaml.dump(config, f, sort_keys=False)

    print(f"Configuration file '{DEFAULT_CONFIG_FILE}' created successfully.")

    os.makedirs(DEFAULT_INPUT_FOLDER, exist_ok=True)
    os.makedirs(DEFAULT_OUTPUT_FOLDER, exist_ok=True)

    print(f"Input and output folders '{DEFAULT_INPUT_FOLDER}' and '{DEFAULT_OUTPUT_FOLDER}' created successfully.")


def append_to_shell_profile(line):
    """
    Append a line to the appropriate shell profile file (.zshrc or .bashrc).

    Args:
        line (str): The line to append to the shell profile.
    """
    shell = os.environ.get("SHELL", "/bin/bash")
    if "zsh" in shell:
        profile_file = os.path.expanduser("~/.zshrc")
    else:
        profile_file = os.path.expanduser("~/.bashrc")

    with open(profile_file, "a") as f:
        f.write(f"\n{line}\n")

    print(f"API key added to {profile_file}")


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files and generate summaries.")
    parser.add_argument("command", nargs="?", choices=["install"], help="Command to execute.")
    parser.add_argument("--input", type=str, default="input", help="Path to the input folder containing audio files.")
    parser.add_argument("--output", type=str, default="output", help="Path to the output folder to save transcriptions and summaries.")
    args = parser.parse_args()

    if args.command == "install":
        install_config()
        return

    input_folder = args.input
    output_folder = args.output

    # Create input and output folders if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    files_transcribed = False

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        output_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")
        try:
            if not os.path.exists(output_file):
                print(f"Transcribing audio file: {file_path}")
                transcribe_audio(file_path, output_file)
                files_transcribed = True
            else:
                with open(output_file, "r", encoding="utf-8") as file:
                    transcription = file.read()

            with open(DEFAULT_CONFIG_FILE, "r") as f:
                config = yaml.safe_load(f)

            openai_models = config["openai"]["models"]
            anthropic_models = config["anthropic"]["models"]

            # Save summaries in markdown files
            for model_config in openai_models:
                openai_summary_file = os.path.join(
                    output_folder,
                    f"{os.path.splitext(filename)[0]} OpenAI Summary (Temp {model_config['temperature']} - {model_config['model']}).md",
                )

                # Skip if summary file already exists
                if os.path.exists(openai_summary_file):
                    continue

                openai_summary = generate_summary(transcription, model_config)

                print(f"OpenAI Summary (Temp {model_config['temperature']} - {model_config['model']}):")
                print(openai_summary)

                # Delete the summary file if it already exists
                if os.path.exists(openai_summary_file):
                    os.remove(openai_summary_file)

                # Write the summary to the file
                with open(openai_summary_file, "w", encoding="utf-8") as file:
                    file.write(openai_summary)

            for model_config in anthropic_models:
                anthropic_summary_file = os.path.join(
                    output_folder,
                    f"{os.path.splitext(filename)[0]} Anthropic Summary (Temp {model_config['temperature']} - {model_config['model']}).md",
                )

                # Skip if summary file already exists
                if os.path.exists(anthropic_summary_file):
                    continue

                anthropic_summary = generate_summary(transcription, model_config)

                print(f"\nAnthropic Summary (Temp {model_config['temperature']} - {model_config['model']}):")
                print(anthropic_summary)

                # Delete the summary file if it already exists
                if os.path.exists(anthropic_summary_file):
                    os.remove(anthropic_summary_file)

                # Write the summary to the file
                with open(anthropic_summary_file, "w", encoding="utf-8") as file:
                    file.write(anthropic_summary)
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")
        finally:
            # Delete the _part* MP3 files
            for file in glob(f"{file_path.partition('.')[0]}_part*.mp3"):
                os.remove(file)

    if not files_transcribed:
        print("Warning: No audio files were transcribed.")


if __name__ == "__main__":
    main()