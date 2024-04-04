import argparse
import os
from glob import glob
from typing import Tuple

import anthropic
import openai
from pydub import AudioSegment
from tqdm import tqdm

# Check if API keys are set
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set")


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
            full_transcription += transcription + "\n\n"
        except Exception as e:
            print(f"An error occurred while transcribing chunk {chunk_file}: {e}")
        finally:
            os.remove(chunk_file)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(full_transcription)


def generate_summary(transcription: str, temperature: float) -> Tuple[str, str]:
    """
    Generate summaries from the transcription using OpenAI and Anthropic models.

    Args:
        transcription (str): The full transcription text.
        temperature (float): Temperature value for controlling randomness in the summaries.

    Returns:
        Tuple[str, str]: OpenAI summary and Anthropic summary.
    """
    input_tokens = len(transcription.split())
    max_tokens = min(int(0.3 * input_tokens), 3000)

    # OpenAI summary
    openai_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise expert but kind to non-technical readers.",
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
        system="Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise expert but kind to non-technical readers.",
        messages=[{"role": "user", "content": transcription}],
    )
    anthropic_summary = anthropic_response.content[0].text

    return openai_summary, anthropic_summary


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files and generate summaries.")
    parser.add_argument("--input", type=str, default="input", help="Path to the input folder containing audio files.")
    parser.add_argument("--output", type=str, default="output", help="Path to the output folder to save transcriptions and summaries.")
    args = parser.parse_args()

    input_folder = args.input
    output_folder = args.output

    # Create input and output folders if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        output_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")
        try:
            if not os.path.exists(output_file):
                print(f"Transcribing audio file: {file_path}")
                transcribe_audio(file_path, output_file)
            else:
                with open(output_file, "r", encoding="utf-8") as file:
                    transcription = file.read()

            # Save summaries in markdown files
            openai_summary_file_03 = os.path.join(output_folder, f"{os.path.splitext(filename)[0]} OpenAI Summary (Temp 0.3).md")
            openai_summary_file_01 = os.path.join(output_folder, f"{os.path.splitext(filename)[0]} OpenAI Summary (Temp 0.1).md")
            openai_summary_file_05 = os.path.join(output_folder, f"{os.path.splitext(filename)[0]} OpenAI Summary (Temp 0.5).md")
            anthropic_summary_file_03 = os.path.join(output_folder, f"{os.path.splitext(filename)[0]} Anthropic Summary (Temp 0.3).md")
            anthropic_summary_file_01 = os.path.join(output_folder, f"{os.path.splitext(filename)[0]} Anthropic Summary (Temp 0.1).md")
            anthropic_summary_file_05 = os.path.join(output_folder, f"{os.path.splitext(filename)[0]} Anthropic Summary (Temp 0.5).md")

            # Skip if summary files already exist
            if all(
                [
                    os.path.exists(openai_summary_file_03),
                    os.path.exists(openai_summary_file_01),
                    os.path.exists(openai_summary_file_05),
                    os.path.exists(anthropic_summary_file_03),
                    os.path.exists(anthropic_summary_file_01),
                    os.path.exists(anthropic_summary_file_05),
                ]
            ):
                print(f"Skipping {filename} - Summary files already exist.")
                continue

            openai_summary_03, anthropic_summary_03 = generate_summary(transcription, temperature=0.3)
            openai_summary_01, anthropic_summary_01 = generate_summary(transcription, temperature=0.1)
            openai_summary_05, anthropic_summary_05 = generate_summary(transcription, temperature=0.5)

            print("OpenAI Summary (Temp 0.3):")
            print(openai_summary_03)
            print("\nAnthropic Summary (Temp 0.3):")
            print(anthropic_summary_03)

            print("OpenAI Summary (Temp 0.1):")
            print(openai_summary_01)
            print("\nAnthropic Summary (Temp 0.1):")
            print(anthropic_summary_01)

            print("OpenAI Summary (Temp 0.5):")
            print(openai_summary_05)
            print("\nAnthropic Summary (Temp 0.5):")
            print(anthropic_summary_05)

            # Delete the summary files if they already exist
            for summary_file in [
                openai_summary_file_03,
                openai_summary_file_01,
                openai_summary_file_05,
                anthropic_summary_file_03,
                anthropic_summary_file_01,
                anthropic_summary_file_05,
            ]:
                if os.path.exists(summary_file):
                    os.remove(summary_file)

            # Write the summaries to the files
            with open(openai_summary_file_03, "w", encoding="utf-8") as file:
                file.write(openai_summary_03)
            with open(openai_summary_file_01, "w", encoding="utf-8") as file:
                file.write(openai_summary_01)
            with open(openai_summary_file_05, "w", encoding="utf-8") as file:
                file.write(openai_summary_05)
            with open(anthropic_summary_file_03, "w", encoding="utf-8") as file:
                file.write(anthropic_summary_03)
            with open(anthropic_summary_file_01, "w", encoding="utf-8") as file:
                file.write(anthropic_summary_01)
            with open(anthropic_summary_file_05, "w", encoding="utf-8") as file:
                file.write(anthropic_summary_05)
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")
        finally:
            # Delete the _part* MP3 files
            for file in glob(f"{file_path.partition('.')[0]}_part*.mp3"):
                os.remove(file)


if __name__ == "__main__":
    main()