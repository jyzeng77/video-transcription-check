#!/usr/bin/env python3
import argparse
import difflib
import os
import sys

import whisper


def transcribe_video(video_path: str, model_name: str = "base") -> str:
    model = whisper.load_model(model_name)
    result = model.transcribe(video_path)
    return result["text"].strip()


def save_transcription(text: str, output_path: str) -> None:
    with open(output_path, "w") as f:
        f.write(text + "\n")


def load_transcription(path: str) -> str:
    with open(path) as f:
        return f.read().strip()


def highlight_diffs(original: str, new: str) -> str:
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile="existing transcription",
        tofile="new transcription",
        lineterm="",
    )
    return "".join(diff)


def print_colored_diff(diff_text: str) -> None:
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"
    for line in diff_text.splitlines():
        if line.startswith("+"):
            print(f"{GREEN}{line}{RESET}")
        elif line.startswith("-"):
            print(f"{RED}{line}{RESET}")
        else:
            print(line)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcribe a video with Whisper and compare it to an existing transcription."
    )
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument(
        "existing_transcription", help="Path to the existing transcription file"
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output path for the new transcription (default: <video_name>_transcript.txt)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"Error: video file not found: {args.video}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.existing_transcription):
        print(
            f"Error: existing transcription file not found: {args.existing_transcription}",
            file=sys.stderr,
        )
        sys.exit(1)

    output_path = args.output or os.path.splitext(args.video)[0] + "_transcript.txt"

    print(f"Transcribing {args.video} with model '{args.model}'...")
    new_text = transcribe_video(args.video, args.model)

    save_transcription(new_text, output_path)
    print(f"New transcription saved to: {output_path}")

    existing_text = load_transcription(args.existing_transcription)

    print("\n--- Differences ---")
    diff_text = highlight_diffs(existing_text, new_text)

    if not diff_text:
        print("No differences found.")
    else:
        print_colored_diff(diff_text)


if __name__ == "__main__":
    main()