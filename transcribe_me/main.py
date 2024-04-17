import argparse
import os
from glob import glob
from typing import Dict, Any
import anthropic
import openai
from pydub import AudioSegment
from tqdm import tqdm
import yaml
from colorama import init, Fore, Style
from halo import Halo
import yamale
from tenacity import retry, wait_exponential, stop_after_attempt
import shutil
import datetime

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DEFAULT_OUTPUT_FOLDER = "output"
DEFAULT_INPUT_FOLDER = "input"
DEFAULT_CONFIG_FILE = ".transcribe.yaml"


def archive_files(input_folder, output_folder):
    """
    Move input and output files to a timestamped folder inside the archive folder.

    Args:
        input_folder (str): Path to the input folder.
        output_folder (str): Path to the output folder.
    """
    archive_folder = "archive"
    if not os.path.exists(archive_folder):
        os.makedirs(archive_folder)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_folder = os.path.join(archive_folder, timestamp)
    os.makedirs(timestamped_folder)

    input_dest = os.path.join(timestamped_folder, "input")
    output_dest = os.path.join(timestamped_folder, "output")
    os.makedirs(input_dest, exist_ok=True)
    os.makedirs(output_dest, exist_ok=True)

    for file_path in glob(os.path.join(input_folder, "*")):
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(input_dest, file_name)
        shutil.move(file_path, dest_path)
        print(f"{Fore.GREEN}Moved {file_path} to {dest_path}")

    for file_path in glob(os.path.join(output_folder, "*")):
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(output_dest, file_name)
        shutil.move(file_path, dest_path)
        print(f"{Fore.GREEN}Moved {file_path} to {dest_path}")

    print(f"{Fore.GREEN}All input and output files have been moved to {timestamped_folder}")

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
    spinner = Halo(text='Splitting audio', spinner='dots')
    spinner.start()
    for i, chunk in enumerate(chunks, start=1):
        chunk_name = f"{os.path.splitext(file_path)[0]}_part{i}.mp3"
        chunk.export(chunk_name, format="mp3")
        chunk_names.append(chunk_name)
    spinner.succeed(f'Audio split into {len(chunk_names)} chunks')

    return chunk_names


@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(5))
def transcribe_chunk(file_path: str) -> str:
    """
    Transcribe an audio chunk using the OpenAI Whisper API.
    Retry with exponential backoff in case of rate limiting.
    """
    with open(file_path, "rb") as audio_file:
        try:
            response = openai.audio.transcriptions.create(language="en", model="whisper-1", file=audio_file)
            return response.text
        except openai.error.RateLimitError as e:
            print(f"{Fore.YELLOW}Rate limit reached, retrying in a bit...")
            raise e
        except Exception as e:
            print(f"{Fore.RED}An error occurred while transcribing {file_path}: {e}")
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

    progress_bar = tqdm(chunk_files, desc="Transcribing", unit="chunk", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}")
    for chunk_file in progress_bar:
        try:
            transcription = transcribe_chunk(chunk_file)
            full_transcription += transcription + " "
        except Exception as e:
            print(f"{Fore.RED}An error occurred while transcribing chunk {chunk_file}: {e}")
        finally:
            os.remove(chunk_file)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(full_transcription)

@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(5))
def generate_summary(transcription: str, platform: str, model_config: Dict[str, Any]) -> str:
    """
    Generate a summary from the transcription using the specified model configuration.
    Retry with exponential backoff in case of rate limiting.
    """
    temperature = model_config["temperature"]
    model_name = model_config["model"]
    system_prompt = model_config["system_prompt"]

    input_tokens = len(transcription.split())
    max_tokens = model_config.get("max_tokens", min(int(0.3 * input_tokens), 3000))

    if "openai" in platform:
        try:
            openai_response = openai.chat.completions.create(
                model=model_name,
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
        except openai.error.RateLimitError as e:
            print(f"{Fore.YELLOW}Rate limit reached, retrying in a bit...")
            raise e
    elif "anthropic" in platform:
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        try:
            anthropic_response = anthropic_client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": transcription}],
            )
            summary = anthropic_response.content[0].text
        except anthropic.error.RateLimitError as e:
            print(f"{Fore.YELLOW}Rate limit reached, retrying in a bit...")
            raise e

    return summary


def install_config():
    """
    Create a config file in the current directory and prompt the user to input API keys if not set.
    """
    print(f"{Fore.GREEN}Welcome to the installation process for Transcribe Me.")
    print(f"{Fore.YELLOW}This will create a configuration file and input/output folders in the current directory.")

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
        print(f"{Fore.YELLOW}Looks like you haven't set your OpenAI API key. We'll set it up for you.")
        openai_key = input(f"{Fore.CYAN}Enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = openai_key
        append_to_shell_profile(f"export OPENAI_API_KEY={openai_key}")

    if not ANTHROPIC_API_KEY:
        print(f"{Fore.YELLOW}Looks like you haven't set your Anthropic API key. We'll set it up for you.")
        anthropic_key = input(f"{Fore.CYAN}Enter your Anthropic API key: ")
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        append_to_shell_profile(f"export ANTHROPIC_API_KEY={anthropic_key}")

    with open(DEFAULT_CONFIG_FILE, "w") as f:
        yaml.dump(config, f, sort_keys=False)

    print(f"{Fore.GREEN}Configuration file '{DEFAULT_CONFIG_FILE}' created successfully.")

    os.makedirs(DEFAULT_INPUT_FOLDER, exist_ok=True)
    os.makedirs(DEFAULT_OUTPUT_FOLDER, exist_ok=True)

    print(f"{Fore.GREEN}Input and output folders '{DEFAULT_INPUT_FOLDER}' and '{DEFAULT_OUTPUT_FOLDER}' created successfully.")
    print(f"{Fore.GREEN}You're all set up!")
    print()
    print(f"{Fore.YELLOW}Usage: simply place your audio files in the '{DEFAULT_INPUT_FOLDER}' folder and `transcribe-me` transcribe and generate summaries in '{DEFAULT_OUTPUT_FOLDER}'.")


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

    print(f"{Fore.GREEN}API key added to {profile_file}")

def read_transcription(output_file: str) -> str:
    """
    Read the transcription from the specified output file.

    Args:
        output_file (str): The path to the output file.

    Returns:
        str: The transcription text.
    """
    with open(output_file, "r", encoding="utf-8") as file:
        transcription = file.read()
        return transcription

def load_config() -> Dict[str, Any]:
    """
    Load the configuration from the default config file.

    Returns:
        dict: The loaded configuration.
    """
    schema_file = os.path.join(os.path.dirname(__file__), "schemas/transcribe.yaml")
    config_file = DEFAULT_CONFIG_FILE

    try:
        schema = yamale.make_schema(schema_file)
        data = yamale.make_data(config_file)
        yamale.validate(schema, data)
        print(f"{Fore.GREEN}Config validation successful!")
    except yamale.YamaleError as e:
        print(f"{Fore.RED}Config validation failed:")
        for result in e.results:
            print(f"{Fore.RED}Error validating data '{result.data}' with '{result.schema}':")
            for error in result.errors:
                print(f"{Fore.RED}\t{error}")
        exit(1)

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files and generate summaries.")
    parser.add_argument("command", nargs="?", choices=["install", "archive"], help="Install the configuration file or archive files.")
    parser.add_argument("--input", type=str, default="input", help="Path to the input folder containing audio files.")
    parser.add_argument("--output", type=str, default="output", help="Path to the output folder to save transcriptions and summaries.")
    args = parser.parse_args()

    if args.command == "install":
        install_config()
        return
    
    if args.command == "archive":
        archive_files(args.input, args.output)
        return
    
    config = load_config()

    input_folder = args.input
    output_folder = args.output

    # Create input and output folders if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    files_transcribed = False

    # Check if the transcribe config file exists
    if not os.path.exists(DEFAULT_CONFIG_FILE):
        print(f"{Fore.RED}Transcribe config file '{DEFAULT_CONFIG_FILE}' does not exist.")
        print(f"{Fore.YELLOW}Please run `transcribe-me install` to create the config file.")
        return

    spinner = Halo(text='Processing audio files', spinner='dots')
    spinner.start()

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        
        if not (filename.endswith(".mp3") or filename.endswith(".m4a")):
            continue

        transcription_name = os.path.splitext(filename)[0]
        output_file = os.path.join(output_folder, f"{transcription_name}.txt")

        try:
            if not os.path.exists(output_file):
                print(f"{Fore.BLUE}Transcribing audio file: {file_path}\n")
                transcribe_audio(file_path, output_file)
                files_transcribed = True
                continue
        except Exception as e:
            print(f"{Fore.RED}An error occurred while processing {file_path}: {e}")
            raise e
        finally:
            # Delete the _part* MP3 files
            for file in glob(f"{file_path.partition('.')[0]}_part*.mp3"):
                os.remove(file)

    for filename in os.listdir(output_folder):
        if not filename.endswith(".txt"):
            continue

        transcription_name = os.path.splitext(filename)[0]
        output_file = os.path.join(output_folder, filename)
        openai_models = config["openai"]["models"]
        anthropic_models = config["anthropic"]["models"]
        transcription = read_transcription(output_file)

        # Save summaries in markdown files
        for model_config in openai_models:
            openai_summary_file = os.path.join(
                output_folder,
                f"{transcription_name} OpenAI Summary (Temp {model_config['temperature']} - {model_config['model']}).md",
            )

            # Skip if summary file already exists
            if os.path.exists(openai_summary_file):
                continue

            print(f"{Fore.BLUE}Summarizing {transcription_name} with OpenAI (Temp {model_config['temperature']} - {model_config['model']}):\n")
            openai_summary = generate_summary(transcription, "openai", model_config)
            print(openai_summary + "\n")

            # Delete the summary file if it already exists
            if os.path.exists(openai_summary_file):
                os.remove(openai_summary_file)

            # Write the summary to the file
            with open(openai_summary_file, "w", encoding="utf-8") as file:
                file.write(openai_summary)

        for model_config in anthropic_models:
            anthropic_summary_file = os.path.join(
                output_folder,
                f"{transcription_name} Anthropic Summary (Temp {model_config['temperature']} - {model_config['model']}).md",
            )

            # Skip if summary file already exists
            if os.path.exists(anthropic_summary_file):
                continue

            print(f"{Fore.BLUE}Summarizing {transcription_name} with Anthropic (Temp {model_config['temperature']} - {model_config['model']}):\n")
            anthropic_summary = generate_summary(transcription, "anthropic", model_config)
            print(anthropic_summary + "\n")

            print(f"\n{Fore.MAGENTA}Anthropic Summary (Temp {model_config['temperature']} - {model_config['model']}):")
            print(anthropic_summary)

            # Delete the summary file if it already exists
            if os.path.exists(anthropic_summary_file):
                os.remove(anthropic_summary_file)

            # Write the summary to the file
            with open(anthropic_summary_file, "w", encoding="utf-8") as file:
                file.write(anthropic_summary)

    spinner.succeed('Audio processing completed')

    if not files_transcribed:
        print(f"{Fore.YELLOW}Warning: No audio files were transcribed.")


if __name__ == "__main__":
    main()