import argparse
from transcribe_me.config import config_manager
from transcribe_me.audio import transcription, splitting
from transcribe_me.summarization import summarizer


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files and generate summaries."
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["install", "archive", "only"],
        help="Install the configuration file or archive files.",
    )
    parser.add_argument(
        "--input",
        type=str,
        default="input",
        help="Path to the input folder containing audio files.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Path to the output folder to save transcriptions and summaries.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.command == "install":
        config_manager.install_config()
        return

    if args.command == "archive":
        config_manager.archive_files(args.input, args.output)
        return

    config = config_manager.load_config()

    input_folder = args.input
    output_folder = args.output

    if args.command == "only":
        transcription.process_audio_files(input_folder, output_folder, config)
        return

    transcription.process_audio_files(input_folder, output_folder, config)
    summarizer.generate_summaries(input_folder, output_folder, config)


if __name__ == "__main__":
    main()
