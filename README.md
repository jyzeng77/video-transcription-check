# Video Transcription And Comparison Tool

## 1 Purpose

This tool transcribes a video file with OpenAI Whisper.
It saves the new transcription to a file.
It then compares the new transcription to an existing transcription.
It shows the differences between the two transcriptions.

## 2 Requirements

- Python 3.8 or later
- A computer with macOS, Linux, or Windows
- An internet connection for the first use of Whisper
- (Optional) A CUDA-capable GPU for faster transcription

## 3 Installation

### 3.1 Quick Setup (Recommended)

Run the setup script. It checks all requirements.

```bash
./setup.sh
```

### 3.2 Manual Setup

#### 3.2.1 Create A Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3.2.2 Install Python Dependencies

Open a terminal.
Move to the directory of the tool.

```bash
pip install -r requirements.txt
```

#### 3.2.3 Install FFmpeg

OpenAI Whisper needs FFmpeg.

**macOS:**

```bash
brew install ffmpeg
```

**Linux (Ubuntu or Debian):**

```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**

Download FFmpeg from https://ffmpeg.org/
Add the FFmpeg `bin` folder to your PATH variable.

## 4 How To Use

You can use the tool in two ways:

- **Guided mode** (recommended for new users)
- **Command-line mode** (for experienced users)

### 4.1 Guided Mode (TUI)

Run the tool with no arguments:

```bash
python main.py
```

The tool guides you through these steps:

1. Select the video file.
2. Select the existing transcription file.
3. Select the Whisper model.
4. Select the output file.
5. Review the summary.
6. Start the transcription.
7. View the differences.

### 4.2 Command-Line Mode

Run the tool with arguments:

```bash
python transcribe_compare.py lecture.mp4 expected_transcript.txt
```

The tool does these steps:

1. It transcribes the video with the default model (`base`).
2. It saves the new transcription to `lecture_transcript.txt`.
3. It compares the new transcription to `expected_transcript.txt`.
4. It shows the differences in the terminal.

### 4.3 Select A Model

You can select a different Whisper model:

```bash
python transcribe_compare.py lecture.mp4 expected_transcript.txt --model medium
```

The available models are: `tiny`, `base`, `small`, `medium`, `large`.

A larger model is more accurate but takes more time.

### 4.4 Select The Output File

You can specify a different output file:

```bash
python transcribe_compare.py lecture.mp4 expected_transcript.txt -o my_output.txt
```

### 4.5 Select The Diff Style

By default the differences are shown inline, laid on top of each other like the
changes view in a word processor. You can also use the classic line-by-line
diff:

```bash
python transcribe_compare.py lecture.mp4 expected_transcript.txt --diff-style classic
```

The available styles are: `inline` (default) and `classic`.

### 4.6 Command-Line Options Reference

| Option | Description |
|---|---|
| `video` | (Positional) Path to the video file to transcribe. |
| `existing_transcription` | (Positional) Path to the existing transcription to compare against. |
| `--model NAME` | Whisper model size: `tiny`, `base`, `small`, `medium`, `large` (default: `base`). |
| `-o`, `--output PATH` | Where to save the new transcription (default: `<video_name>_transcript.txt`). |
| `--diff-style STYLE` | How to show the differences: `inline` (default) or `classic`. |

Example using every option:

```bash
python transcribe_compare.py lecture.mp4 expected_transcript.txt \
  --model medium -o my_output.txt --diff-style inline
```

## 5 How To Read The Differences

In the default **inline** view, the changes are laid on top of each other so you
can read the transcription naturally:

- Text with **no** marker is unchanged.
- Text in **green** with `[+ ... +]` was **added** in the new transcription.
- Text in **red** with `[- ... -]` was **removed** from the existing
  transcription and is shown with a strikethrough.

Example:

```text
Legend: [+ added text +]  [- removed text -]
the quick [-brown-][+red+] fox [-jumps-][+leaps+] over the [-lazy-][+sleepy+] dog
```

If a whole line was added or removed, the entire line is wrapped in the
corresponding markers.

The `[- ... -]` and `[+ ... +]` symbols are always present, so the diff stays
readable even when colors are not supported or the output is saved to a file.

In the `classic` view, lines follow the standard diff format:

- Lines in **green** with a `+` are in the new transcription only.
- Lines in **red** with a `-` are in the existing transcription only.
- Lines with no color and no `+` or `-` are equal in both transcriptions.

## 6 Output

The tool creates a text file with the new transcription.
The name of the file is `<video_name>_transcript.txt`.
You can change this name with the `-o` option.

## 7 Troubleshooting

| Problem | Solution |
|---|---|
| "setup.sh not found" | Move to the directory of the tool. Run `./setup.sh`. |
| "command not found: ./setup.sh" | Run `chmod +x setup.sh` first. |
| "video file not found" | Check that the path to the video file is correct. |
| "existing transcription file not found" | Check that the path to the existing transcription file is correct. |
| Whisper downloads a model each time | This is normal. The model is cached after the first download. |
| FFmpeg is not found | Install FFmpeg. See Section 3.2. |

## 8 Testing

The test suite uses Python's built-in `unittest` module. No extra packages are
needed. Run it from the project directory:

```bash
venv/bin/python -m unittest discover -s tests -v
```

The tests cover the diff logic, symbol rendering, file input/output, and the
command-line flow (with transcription mocked out).

