import argparse
import os
from glob import glob
from typing import Tuple

import anthropic
import openai
from pydub import AudioSegment
from tqdm import tqdm
import yaml

# Check if API keys are set
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")


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


def generate_summary(transcription: str, temperature: float, max_tokens: int) -> Tuple[str, str]:
    """
    Generate summaries from the transcription using OpenAI and Anthropic models.

    Args:
        transcription (str): The full transcription text.
        temperature (float): Temperature value for controlling randomness in the summaries.
        max_tokens (int): Maximum number of tokens for the summaries.

    Returns:
        Tuple[str, str]: OpenAI summary and Anthropic summary.
    """
    input_tokens = len(transcription.split())
    max_tokens = min(max_tokens, 3000)

    # OpenAI summary
    openai_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.",
            },
            {"role": "user", "content": transcription},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    openai_summary = openai_response.choices[0].message.content.strip()

    # Anthropic summary
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    anthropic_response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=max_tokens,
        temperature=temperature,
        system="Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.",
        messages=[{"role": "user", "content": transcription}],
    )
    anthropic_summary = anthropic_response.content[0].text

    return openai_summary, anthropic_summary


def install_config():
    """
    Create a .transcribe.yaml file in the current directory and prompt the user to input API keys if not set.
    """
    config = {
        "openai": {"temperature": 0.3, "max_tokens": 1000},
        "anthropic": {"temperature": 0.3, "max_tokens": 1000},
        "input_folder": "input",
        "output_folder": "output",
    }

    if not OPENAI_API_KEY:
        openai_key = input("Enter your OpenAI API key: ")
        config["openai"]["api_key"] = openai_key
        append_to_shell_profile(f"export OPENAI_API_KEY={openai_key}")

    if not ANTHROPIC_API_KEY:
        anthropic_key = input("Enter your Anthropic API key: ")
        config["anthropic"]["api_key"] = anthropic_key
        append_to_shell_profile(f"export ANTHROPIC_API_KEY={anthropic_key}")

    with open(".transcribe.yaml", "w") as f:
        yaml.dump(config, f)

    print("Configuration file '.transcribe.yaml' created successfully.")


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
    parser.add_argument("--install", action="store_true", help="Install and configure the application.")
    parser.add_argument("--input", type=str, default="input", help="Path to the input folder containing audio files.")
    parser.add_argument("--output", type=str, default="output", help="Path to the output folder to save transcriptions and summaries.")
    args = parser.parse_args()

    if args.install:
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

            # Load configuration from .transcribe.yaml
            with open(".transcribe.yaml", "r") as f:
                config = yaml.safe_load(f)

            openai_temp = config["openai"]["temperature"]
            anthropic_temp = config["anthropic"]["temperature"]
            openai_max_tokens = config["openai"]["max_tokens"]
            anthropic_max_tokens = config["anthropic"]["max_tokens"]

            # Save summaries in markdown files
            openai_summary_file_03 = os.path.join(output_folder, f"{os.path.splitext(filename)[0]} OpenAI Summary (Temp {openai_temp}).md")
            anthropic_summary_file_03 = os.path.join(output_folder, f"{os.path.splitext(filename)[0]} Anthropic Summary (Temp {anthropic_temp}).md")

            # Skip if summary files already exist
            if os.path.exists(openai_summary_file_03) and os.path.exists(anthropic_summary_file_03):
                print(f"Skipping {filename} - Summary files already exist.")
                continue

            openai_summary, anthropic_summary = generate_summary(transcription, openai_temp, openai_max_tokens)

            print(f"OpenAI Summary (Temp {openai_temp}):")
            print(openai_summary)
            print(f"\nAnthropic Summary (Temp {anthropic_temp}):")
            print(anthropic_summary)

            # Delete the summary files if they already exist
            if os.path.exists(openai_summary_file_03):
                os.remove(openai_summary_file_03)
            if os.path.exists(anthropic_summary_file_03):
                os.remove(anthropic_summary_file_03)

            # Write the summaries to the files
            with open(openai_summary_file_03, "w", encoding="utf-8") as file:
                file.write(openai_summary)
            with open(anthropic_summary_file_03, "w", encoding="utf-8") as file:
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