#!/usr/bin/env python3
import os
import sys

from transcribe_compare import (
    load_transcription,
    save_transcription,
    show_diffs,
    transcribe_video,
)

MODELS = ["tiny", "base", "small", "medium", "large"]

BANNER = r"""
╔══════════════════════════════════════════════════════════╗
║        Video Transcription And Comparison Tool          ║
╚══════════════════════════════════════════════════════════╝
"""


def prompt_file(message: str, must_exist: bool = True) -> str:
    while True:
        path = input(f"  {message}: ").strip()
        if not path:
            print("  Path cannot be empty. Try again.")
            continue
        if must_exist and not os.path.exists(path):
            print(f"  File not found: {path}. Try again.")
            continue
        return path


def prompt_model() -> str:
    print("  Available models:")
    for i, name in enumerate(MODELS, 1):
        tag = " (recommended)" if name == "base" else ""
        print(f"    {i}) {name}{tag}")
    while True:
        choice = input("  Select model [2]: ").strip()
        if choice == "":
            return "base"
        if choice.isdigit() and 1 <= int(choice) <= len(MODELS):
            return MODELS[int(choice) - 1]
        print("  Invalid choice. Enter a number from 1 to 5.")


def prompt_output(default: str) -> str:
    path = input(f"  Output file [{default}]: ").strip()
    return path if path else default


def confirm(message: str) -> bool:
    answer = input(f"  {message} [Y/n]: ").strip().lower()
    return answer in ("", "y", "yes")


def main() -> None:
    print(BANNER)

    print("Step 1: Select the video file.")
    video = prompt_file("Path to video file")

    print("\nStep 2: Select the existing transcription file.")
    existing = prompt_file("Path to existing transcription file")

    print("\nStep 3: Select the Whisper model.")
    model = prompt_model()

    default_output = os.path.splitext(video)[0] + "_transcript.txt"
    print("\nStep 4: Select the output file.")
    output = prompt_output(default_output)

    print("\n--- Summary ---")
    print(f"  Video:            {video}")
    print(f"  Existing:         {existing}")
    print(f"  Model:            {model}")
    print(f"  Output:           {output}")
    print()

    if not confirm("Start transcription?"):
        print("  Cancelled.")
        sys.exit(0)

    print(f"\nTranscribing {video} with model '{model}'...")
    new_text = transcribe_video(video, model)

    save_transcription(new_text, output)
    print(f"New transcription saved to: {output}")

    existing_text = load_transcription(existing)

    show_diffs(existing_text, new_text)

    print("\nDone.")


if __name__ == "__main__":
    main()
