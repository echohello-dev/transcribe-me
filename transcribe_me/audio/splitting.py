import os
from pydub import AudioSegment
from halo import Halo


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
    chunks = [audio[i : i + interval_ms] for i in range(0, len(audio), interval_ms)]

    chunk_names = []
    spinner = Halo(text="Splitting audio", spinner="dots")
    spinner.start()
    for i, chunk in enumerate(chunks, start=1):
        chunk_name = f"{os.path.splitext(file_path)[0]}_part{i}.mp3"
        chunk.export(chunk_name, format="mp3")
        chunk_names.append(chunk_name)
    spinner.succeed(f"Audio split into {len(chunk_names)} chunks")

    return chunk_names
