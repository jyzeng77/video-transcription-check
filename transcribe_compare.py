#!/usr/bin/env python3
import argparse
import difflib
import os
import re
import sys

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
STRIKETHROUGH = "\033[9m"


def transcribe_video(video_path: str, model_name: str = "base") -> str:
    import whisper

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
    for line in diff_text.splitlines():
        if line.startswith("+"):
            print(f"{GREEN}{line}{RESET}")
        elif line.startswith("-"):
            print(f"{RED}{line}{RESET}")
        else:
            print(line)


def diff_segments(original: str, new: str) -> list:
    """Compare two texts word by word.

    Returns a list of (kind, text) segments where kind is one of
    "equal", "delete", or "insert".
    """
    old_tokens = re.findall(r"\s+|\S+", original)
    new_tokens = re.findall(r"\s+|\S+", new)
    matcher = difflib.SequenceMatcher(None, old_tokens, new_tokens, autojunk=False)
    segments = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            segments.append(("equal", "".join(old_tokens[i1:i2])))
        elif tag == "delete":
            segments.append(("delete", "".join(old_tokens[i1:i2])))
        elif tag == "insert":
            segments.append(("insert", "".join(new_tokens[j1:j2])))
        else:  # replace
            segments.append(("delete", "".join(old_tokens[i1:i2])))
            segments.append(("insert", "".join(new_tokens[j1:j2])))
    return segments


def build_inline_diff(original: str, new: str) -> list:
    """Compare two transcriptions and lay the changes on top of each other.

    Unchanged lines are kept as-is. Changed lines are shown inline: removed
    text is wrapped in ``[- ... -]`` and added text in ``[+ ... +]``.
    """
    old_lines = original.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    segments = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for line in old_lines[i1:i2]:
                segments.append(("equal", line))
        elif tag == "delete":
            for line in old_lines[i1:i2]:
                segments.append(("delete", line))
        elif tag == "insert":
            for line in new_lines[j1:j2]:
                segments.append(("insert", line))
        else:  # replace
            old_block = "".join(old_lines[i1:i2])
            new_block = "".join(new_lines[j1:j2])
            segments.extend(diff_segments(old_block, new_block))
    return segments


def _symbolize(text: str, open_symbol: str, close_symbol: str) -> str:
    result = []
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\n")
        if content:
            result.append(f"{open_symbol}{content}{close_symbol}")
        if line.endswith("\n"):
            result.append("\n")
    return "".join(result)


def render_diffs(segments: list) -> str:
    """Render diff segments to plain text using [+ ... +] and [- ... -] symbols."""
    out = []
    for kind, text in segments:
        if kind == "equal":
            out.append(text)
        elif kind == "delete":
            out.append(_symbolize(text, "[-", "-]"))
        else:
            out.append(_symbolize(text, "[+", "+]"))
    return "".join(out)


def _colorize(text: str, code: str, open_symbol: str, close_symbol: str) -> str:
    result = []
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\n")
        if content:
            result.append(f"{code}{open_symbol}{content}{close_symbol}{RESET}")
        if line.endswith("\n"):
            result.append("\n")
    return "".join(result)


def print_diff_legend() -> None:
    print(
        f"Legend: {GREEN}[+ added text +]{RESET}  "
        f"{RED}{STRIKETHROUGH}[- removed text -]{RESET}"
    )


def print_inline_diff(segments: list) -> None:
    for kind, text in segments:
        if kind == "equal":
            sys.stdout.write(text)
        elif kind == "delete":
            sys.stdout.write(_colorize(text, RED + STRIKETHROUGH, "[-", "-]"))
        else:
            sys.stdout.write(_colorize(text, GREEN, "[+", "+]"))
    if not segments or not segments[-1][1].endswith("\n"):
        sys.stdout.write("\n")


def show_diffs(existing_text: str, new_text: str, diff_style: str = "inline") -> None:
    print("\n--- Differences ---")
    if existing_text == new_text:
        print("No differences found.")
        return
    if diff_style == "classic":
        diff_text = highlight_diffs(existing_text, new_text)
        if diff_text:
            print_colored_diff(diff_text)
    else:
        print_diff_legend()
        print_inline_diff(build_inline_diff(existing_text, new_text))


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
    parser.add_argument(
        "--diff-style",
        default="inline",
        choices=["inline", "classic"],
        help="How to show the differences (default: inline)",
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

    show_diffs(existing_text, new_text, args.diff_style)


if __name__ == "__main__":
    main()