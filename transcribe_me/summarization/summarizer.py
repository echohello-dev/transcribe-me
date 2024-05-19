from typing import Dict, Any
import openai
import anthropic
from colorama import Fore
from tenacity import retry, wait_exponential, stop_after_attempt
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")


@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(5))
def generate_summary(
    transcription: str, platform: str, model_config: Dict[str, Any]
) -> str:
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
        except e:
            print(f"{Fore.RED}Error: {e}")
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
        except e:
            print(f"{Fore.RED}Error: {e}")
    return summary


def generate_summaries(
    input_folder: str, output_folder: str, config: Dict[str, Any]
) -> None:
    """
    Generate summaries for transcribed files in the output folder using the specified configuration.

    Args:
        input_folder (str): Path to the input folder containing audio files.
        output_folder (str): Path to the output folder containing transcriptions.
        config (Dict[str, Any]): Configuration dictionary.
    """
    for filename in os.listdir(output_folder):
        if not filename.endswith(".txt"):
            continue

        transcription_name = os.path.splitext(filename)[0]
        output_file = os.path.join(output_folder, filename)
        openai_models = config["openai"]["models"]
        anthropic_models = config["anthropic"]["models"]

        with open(output_file, "r", encoding="utf-8") as file:
            transcription = file.read()

        # Save summaries in markdown files
        for model_config in openai_models:
            openai_summary_file = os.path.join(
                output_folder,
                f"{transcription_name} OpenAI Summary (Temp {model_config['temperature']} - {model_config['model']}).md",
            )

            # Skip if summary file already exists
            if os.path.exists(openai_summary_file):
                continue

            print(
                f"{Fore.BLUE}Summarizing {transcription_name} with OpenAI (Temp {model_config['temperature']} - {model_config['model']}):\n"
            )
            openai_summary = generate_summary(transcription, "openai", model_config)
            print(openai_summary + "\n")

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

            print(
                f"{Fore.BLUE}Summarizing {transcription_name} with Anthropic (Temp {model_config['temperature']} - {model_config['model']}):\n"
            )
            anthropic_summary = generate_summary(
                transcription, "anthropic", model_config
            )
            print(anthropic_summary + "\n")

            # Write the summary to the file
            with open(anthropic_summary_file, "w", encoding="utf-8") as file:
                file.write(anthropic_summary)
