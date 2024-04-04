from glob import glob
import anthropic
import openai
from pydub import AudioSegment
import os
from tqdm import tqdm

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set")
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY is not set")

def split_mp3(file_path, interval_minutes=10):
    """
    Split an MP3 file into chunks of a specified length.

    Args:
        file_path: Path to the MP3 file to split.
        interval_minutes: Length of each chunk in minutes.
    """

    if file_path.endswith(".m4a"):
        audio = AudioSegment.from_file(file_path, format="m4a")
    else:
        audio = AudioSegment.from_mp3(file_path)

    interval_ms = interval_minutes * 60 * 1000
    chunks = [audio[i : i + interval_ms] for i in range(0, len(audio), interval_ms)]

    chunk_names = []
    for i, chunk in enumerate(tqdm(chunks, desc="Splitting audio")):
        chunk_name = f"{file_path.partition('.')[0]}_part{i+1}.mp3"
        chunk.export(chunk_name, format="mp3")
        chunk_names.append(chunk_name)
        print(f"Exported chunk: {chunk_name}")

    return chunk_names


def transcribe_with_whisper_api(file_path):
    """
    Transcribe an audio file using the OpenAI Whisper API.

    Args:
        file_path: Path to the audio file to transcribe.
    """

    with open(file_path, "rb") as audio_file:
        try:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )

            return response.text
        except Exception as e:
            print(f"An error occurred while transcribing {file_path}: {e}")
            raise e


def transcribe_full_audio(file_path, output_file):
    """
    Transcribe a full audio file using the OpenAI Whisper API.

    Args:
        file_path: Path to the audio file to transcribe.
        output_file: Path to the file to save the transcript to.
    """

    chunk_files = split_mp3(file_path)
    full_transcription = ""

    for i, chunk_file in enumerate(chunk_files):
        print(f"Transcribing chunk {i+1}/{len(chunk_files)}...")
        with tqdm(total=len(chunk_files), desc="Transcribing") as pbar:
            try:
                transcription = transcribe_with_whisper_api(chunk_file)
                full_transcription += transcription + "\n\n"
            except Exception as e:
                print(f"An error occurred while transcribing chunk {i+1}: {e}")
                raise e
            finally:
                os.remove(chunk_file)
            pbar.update(1)

    with open(output_file, "w") as file:
        file.write(full_transcription)

    print(f"Transcription complete. Full transcript saved to '{output_file}'")


def generate_summary(transcription, temperature=0.3):
    """
    Generate a summary from the transcription.

    Args:
        transcription: The full transcription text.

    Returns:
        The generated summary.
    """
    input_tokens = len(transcription.split())
    max_tokens = min(int(0.3 * input_tokens), 3000)

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
        temperature=0.3,
        max_tokens=max_tokens,
    )
    openai_summary = openai_response.choices[0].message.content.strip()

    # Anthropic summary
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    anthropic_response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=max_tokens,
        temperature=0.3,
        system="Generate a summary with key points in bold and a Next Steps section, use Markdown, be a concise tech expert but kind to non-technical readers.",
        messages=[
            {"role": "user", "content": transcription},
        ],
    )
    anthropic_summary = anthropic_response.content[0].text

    return openai_summary, anthropic_summary


def main():
    input_folder = "input"
    output_folder = "output"

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        output_file = os.path.join(
            output_folder, f"{os.path.splitext(filename)[0]}.txt"
        )
        try:
            if not os.path.exists(output_file):
                print(f"Transcribing audio file: {file_path}")
                transcription = transcribe_full_audio(
                    file_path,
                    output_file,
                )
            else:
                with open(output_file, "r") as file:
                    transcription = file.read()

            # Save summaries in markdown files
            openai_summary_file_03 = os.path.join(
                output_folder,
                f"{os.path.splitext(filename)[0]} OpenAI Summary (Temp 0.3).md",
            )
            openai_summary_file_01 = os.path.join(
                output_folder,
                f"{os.path.splitext(filename)[0]} OpenAI Summary (Temp 0.1).md",
            )
            openai_summary_file_05 = os.path.join(
                output_folder,
                f"{os.path.splitext(filename)[0]} OpenAI Summary (Temp 0.5).md",
            )
            anthropic_summary_file_03 = os.path.join(
                output_folder,
                f"{os.path.splitext(filename)[0]} Anthropic Summary (Temp 0.3).md",
            )
            anthropic_summary_file_01 = os.path.join(
                output_folder,
                f"{os.path.splitext(filename)[0]} Anthropic Summary (Temp 0.1).md",
            )
            anthropic_summary_file_05 = os.path.join(
                output_folder,
                f"{os.path.splitext(filename)[0]} Anthropic Summary (Temp 0.5).md",
            )

            # Skip if summary files already exist
            if (
                os.path.exists(openai_summary_file_03)
                and os.path.exists(openai_summary_file_01)
                and os.path.exists(openai_summary_file_05)
                and os.path.exists(anthropic_summary_file_03)
                and os.path.exists(anthropic_summary_file_01)
                and os.path.exists(anthropic_summary_file_05)
            ):
                print(f"Skipping {filename} - Summary files already exist.")
                continue

            openai_summary_03, anthropic_summary_03 = generate_summary(
                transcription, temperature=0.3
            )
            openai_summary_01, anthropic_summary_01 = generate_summary(
                transcription, temperature=0.1
            )
            openai_summary_05, anthropic_summary_05 = generate_summary(
                transcription, temperature=0.5
            )

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
            if os.path.exists(openai_summary_file_03):
                os.remove(openai_summary_file_03)
            if os.path.exists(openai_summary_file_01):
                os.remove(openai_summary_file_01)
            if os.path.exists(openai_summary_file_05):
                os.remove(openai_summary_file_05)
            if os.path.exists(anthropic_summary_file_03):
                os.remove(anthropic_summary_file_03)
            if os.path.exists(anthropic_summary_file_01):
                os.remove(anthropic_summary_file_01)
            if os.path.exists(anthropic_summary_file_05):
                os.remove(anthropic_summary_file_05)

            # Write the summaries to the files
            with open(openai_summary_file_03, "w") as file:
                file.write(openai_summary_03)
            with open(openai_summary_file_01, "w") as file:
                file.write(openai_summary_01)
            with open(openai_summary_file_05, "w") as file:
                file.write(openai_summary_05)
            with open(anthropic_summary_file_03, "w") as file:
                file.write(anthropic_summary_03)
            with open(anthropic_summary_file_01, "w") as file:
                file.write(anthropic_summary_01)
            with open(anthropic_summary_file_05, "w") as file:
                file.write(anthropic_summary_05)
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")
            raise e
        finally:
            # Delete the _part* MP3 files
            for file in glob(f"{file_path.partition('.')[0]}_part*.mp3"):
                os.remove(file)


if __name__ == "__main__":
    main()
