import os
from glob import glob
from typing import Dict, Any
import openai
import assemblyai as aai
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


def transcribe_audio(file_path: str, output_path: str, config: Dict[str, Any]) -> None:
    """
    Transcribe an audio file using either OpenAI Whisper API or AssemblyAI.

    Args:
        file_path (str): Path to the audio file to transcribe.
        output_path (str): Path to the output file for the transcription.
        config (Dict[str, Any]): Configuration dictionary.
    """
    use_assemblyai = config.get("use_assemblyai", False)

    if use_assemblyai:
        transcribe_with_assemblyai(file_path, output_path, config)
    else:
        transcribe_with_openai(file_path, output_path)


def transcribe_with_openai(file_path: str, output_path: str) -> None:
    """
    Transcribe an audio file using the OpenAI Whisper API.
    """
    chunk_files = split_audio(file_path)
    full_transcription = ""

    progress_bar = tqdm(
        chunk_files,
        desc="Transcribing with OpenAI",
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


def transcribe_with_assemblyai(
    file_path: str, output_path: str, config: Dict[str, Any]
) -> None:
    """
    Transcribe an audio file using AssemblyAI.
    """
    transcription_config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.nano,
        speaker_labels=True,
        summarization=True,
        sentiment_analysis=True,
        auto_highlights=True,
        iab_categories=True,
    )
    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe(file_path, config=transcription_config)

    # Write transcription to file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(transcript.text)

    # Write additional information to separate files
    base_name = os.path.splitext(output_path)[0]

    # Speaker Diarization
    with open(f"{base_name}_speakers.txt", "w", encoding="utf-8") as file:
        for utterance in transcript.utterances:
            file.write(f"Speaker {utterance.speaker}: {utterance.text}\n")
    # Summary
    with open(f"{base_name}_summary.txt", "w", encoding="utf-8") as file:
        file.write(transcript.summary)

    # Sentiment Analysis
    with open(f"{base_name}_sentiment.txt", "w", encoding="utf-8") as file:
        for result in transcript.sentiment_analysis:
            file.write(f"Text: {result.text}\n")
            file.write(f"Sentiment: {result.sentiment}\n")
            file.write(f"Confidence: {result.confidence}\n")
            file.write(f"Timestamp: {result.start} - {result.end}\n\n")

    # Key Phrases
    with open(f"{base_name}_key_phrases.txt", "w", encoding="utf-8") as file:
        for phrase in transcript.auto_highlights_result.results:
            file.write(f"Highlight: {phrase.text}\n")
            file.write(f"Count: {phrase.count}\n")
            file.write(f"Rank: {phrase.rank}\n")

    # Topic Detection
    if transcript.iab_categories:
        with open(f"{base_name}_topics.txt", "w", encoding="utf-8") as file:
            # Detailed results
            file.write("Detailed Topic Results:\n")
            for result in transcript.iab_categories.results:
                file.write(f"Text: {result.text}\n")
                file.write(
                    f"Timestamp: {result.timestamp.start} - {result.timestamp.end}\n"
                )
                for label in result.labels:
                    file.write(f"  {label.label} (Relevance: {label.relevance})\n")
                file.write("\n")

            # Summary of all topics
            file.write("\nTopic Summary:\n")
            for topic, relevance in transcript.iab_categories.summary.items():
                file.write(f"Audio is {relevance * 100:.2f}% relevant to {topic}\n")


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
                transcribe_audio(file_path, output_file, config)
        except Exception as e:
            print(f"{Fore.RED}An error occurred while processing {file_path}: {e}")
            raise e
        finally:
            # Delete the _part* MP3 files if using OpenAI
            if not config.get("use_assemblyai", False):
                for file in glob(f"{file_path.partition('.')[0]}_part*.mp3"):
                    os.remove(file)
