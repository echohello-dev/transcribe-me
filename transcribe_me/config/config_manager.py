import os
import shutil
import datetime
from glob import glob
from typing import Dict, Any
import yaml
import yamale
from colorama import Fore

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

DEFAULT_OUTPUT_FOLDER = "output"
DEFAULT_INPUT_FOLDER = "input"
DEFAULT_CONFIG_FILE = ".transcribe.yaml"


def archive_files(input_folder: str, output_folder: str) -> None:
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

    print(
        f"{Fore.GREEN}All input and output files have been moved to {timestamped_folder}"
    )


def install_config() -> None:
    """
    Create a config file in the current directory and prompt the user to input API keys if not set.
    """
    print(f"{Fore.GREEN}Welcome to the installation process for Transcribe Me.")
    print(
        f"{Fore.YELLOW}This will create a configuration file and input/output folders in the current directory."
    )

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
        print(
            f"{Fore.YELLOW}Looks like you haven't set your OpenAI API key. We'll set it up for you."
        )
        openai_key = input(f"{Fore.CYAN}Enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = openai_key
        append_to_shell_profile(f"export OPENAI_API_KEY={openai_key}")

    if not ANTHROPIC_API_KEY:
        print(
            f"{Fore.YELLOW}Looks like you haven't set your Anthropic API key. We'll set it up for you."
        )
        anthropic_key = input(f"{Fore.CYAN}Enter your Anthropic API key: ")
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        append_to_shell_profile(f"export ANTHROPIC_API_KEY={anthropic_key}")

    with open(DEFAULT_CONFIG_FILE, "w") as f:
        yaml.dump(config, f, sort_keys=False)

    print(
        f"{Fore.GREEN}Configuration file '{DEFAULT_CONFIG_FILE}' created successfully."
    )

    os.makedirs(DEFAULT_INPUT_FOLDER, exist_ok=True)
    os.makedirs(DEFAULT_OUTPUT_FOLDER, exist_ok=True)

    print(
        f"{Fore.GREEN}Input and output folders '{DEFAULT_INPUT_FOLDER}' and '{DEFAULT_OUTPUT_FOLDER}' created successfully."
    )
    print(f"{Fore.GREEN}You're all set up!")
    print()
    print(
        f"{Fore.YELLOW}Usage: simply place your audio files in the '{DEFAULT_INPUT_FOLDER}' folder and `transcribe-me` transcribe and generate summaries in '{DEFAULT_OUTPUT_FOLDER}'."
    )


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


def load_config() -> Dict[str, Any]:
    """
    Load the configuration from the default config file.

    Returns:
        dict: The loaded configuration.
    """
    schema_file = os.path.join(os.path.dirname(__file__), "schema.yaml")
    config_file = DEFAULT_CONFIG_FILE

    try:
        schema = yamale.make_schema(schema_file)
        data = yamale.make_data(config_file)
        yamale.validate(schema, data)
        print(f"{Fore.GREEN}Config validation successful!")
    except yamale.YamaleError as e:
        print(f"{Fore.RED}Config validation failed:")
        for result in e.results:
            print(
                f"{Fore.RED}Error validating data '{result.data}' with '{result.schema}':"
            )
            for error in result.errors:
                print(f"{Fore.RED}\t{error}")
        exit(1)

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config
