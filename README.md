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

### 3.1 Install Python Dependencies

Open a terminal.
Move to the directory of the tool.

```bash
pip install -r requirements.txt
```

### 3.2 Install FFmpeg

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

### 4.1 Prepare Your Files

You need:

- A video file (for example, `lecture.mp4`)
- A text file with the existing transcription (for example, `expected_transcript.txt`)

### 4.2 Run The Tool

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

## 5 How To Read The Differences

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
| "video file not found" | Check that the path to the video file is correct. |
| "existing transcription file not found" | Check that the path to the existing transcription file is correct. |
| Whisper downloads a model each time | This is normal. The model is cached after the first download. |
| FFmpeg is not found | Install FFmpeg. See Section 3.2. |

