import os
from glob import glob
from typing import Dict, Any
import openai
from tqdm import tqdm
from colorama import Fore
from tenacity import retry, wait_exponential, stop_after_attempt

from .splitting import split_audio


@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(5))
def transcribe_chunk(file_path: str) -> str:
    """
    Transcribe an audio chunk using the OpenAI Whisper API.
    Retry with exponential backoff in case of rate limiting.
    """
    with open(file_path, "rb") as audio_file:
        try:
            response = openai.audio.transcriptions.create(
                language="en", model="whisper-1", file=audio_file
            )
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

    progress_bar = tqdm(
        chunk_files,
        desc="Transcribing",
        unit="chunk",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
    )
    for chunk_file in progress_bar:
        try:
            transcription = transcribe_chunk(chunk_file)
            full_transcription += transcription + " "
        except Exception as e:
            print(
                f"{Fore.RED}An error occurred while transcribing chunk {chunk_file}: {e}"
            )
        finally:
            os.remove(chunk_file)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(full_transcription)


def process_audio_files(
    input_folder: str, output_folder: str, config: Dict[str, Any]
) -> None:
    """
    Process audio files in the input folder, transcribe them, and save the transcriptions in the output folder.

    Args:
        input_folder (str): Path to the input folder containing audio files.
        output_folder (str): Path to the output folder to save transcriptions.
        config (Dict[str, Any]): Configuration dictionary.
    """
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
        except Exception as e:
            print(f"{Fore.RED}An error occurred while processing {file_path}: {e}")
            raise e
        finally:
            # Delete the _part* MP3 files
            for file in glob(f"{file_path.partition('.')[0]}_part*.mp3"):
                os.remove(file)
