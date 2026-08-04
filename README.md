# Video Transcription And Comparison Tool

## 1 What This Tool Does

This tool turns a video file into text (a transcript), then compares that new
text with a text file you already have — for example, the transcript from a
previous version of the video.

It shows you exactly what changed between the two versions. If you want, it can
also combine both versions into one clean final transcript.

## 2 Quickstart

The fastest way to start. Three steps:

**Step 1 — Run the one-time setup.**

Open a terminal, go to the folder where you saved this tool, and run:

```bash
./setup.sh
```

This checks your computer, installs what is needed, and downloads a small local
AI model (about 1 GB, only once). The first run may take a few minutes.

**Step 2 — Start the tool.**

```bash
python3 main.py
```

**Step 3 — Follow the questions on screen.**

The tool will ask you for:

1. Your video file
2. Your existing transcript file
3. Which AI model to use (press Enter to use the recommended one)

Then it transcribes the video, shows you the differences, and asks if you want
to combine both transcripts into one final version.

That's it. You do not need to remember any commands.

## 3 What You Will See

The differences are shown like "tracked changes" in a word processor:

- Plain text — the same in both versions
- Green with `[+ ... +]` — text that was added in the new version
- Red with `[- ... -]` — text that was removed

Example:

```text
the quick [-brown-][+red+] fox [-jumps-][+leaps+] over the [-lazy-][+sleepy+] dog
```

Files the tool creates:

- `<video_name>_transcript.txt` — the new transcription
- `<video_name>_merged.txt` — the combined final version (only if you choose to merge)

## 4 Set Things Up Yourself (Optional)

Only use this if you prefer to set things up by hand instead of running
`./setup.sh`. Otherwise, skip this section.

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install the Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install FFmpeg (needed to transcribe audio):

   - **macOS:** `brew install ffmpeg`
   - **Linux (Ubuntu or Debian):** `sudo apt update && sudo apt install ffmpeg`
   - **Windows:** Download FFmpeg from https://ffmpeg.org/ and add its `bin` folder to your PATH

4. If you want to use the merge feature, install
   [llama.cpp](https://github.com/ggml-org/llama.cpp) and download a GGUF model
   into the `models` folder. `setup.sh` does this for you automatically.

## 5 Using The Tool

### 5.1 Guided Mode (for everyone)

Start the tool with no arguments:

```bash
python3 main.py
```

It guides you through each step by asking questions. This is the easiest way to
use the tool.

### 5.2 Command-Line Mode (for those who like typing)

You can do the whole thing in one command:

```bash
python3 transcribe_compare.py lecture.mp4 expected_transcript.txt
```

This transcribes `lecture.mp4`, saves the new text to
`lecture_transcript.txt`, and compares it with `expected_transcript.txt`.

### 5.3 Combine Two Transcripts

To get one clean final transcript from both versions, add `--merge`:

```bash
python3 transcribe_compare.py lecture.mp4 expected_transcript.txt --merge
```

The combined transcript is printed and saved to `lecture_merged.txt`.

Everything runs on your computer. No data leaves your machine, and no API key
is needed. The bundled model (`Qwen2.5-1.5B`) is downloaded once by
`setup.sh` and is only in memory while it works.

### 5.4 All Command-Line Options

| Option | What it does |
|---|---|
| `video` | The video file to transcribe. |
| `existing_transcription` | The existing transcript to compare against. |
| `--model NAME` | Which transcription model to use: `tiny`, `base`, `small`, `medium`, `large` (default: `base`). |
| `-o`, `--output PATH` | Where to save the new transcript (default: `<video_name>_transcript.txt`). |
| `--diff-style STYLE` | How to show changes: `inline` (default) or `classic`. |
| `--merge` | Combine both transcripts into one final version. |
| `--merge-model PATH` | The local model file to use for merging (default: the one from `setup.sh`). |
| `--merge-output PATH` | Where to save the merged transcript (default: `<video_name>_merged.txt`). |

## 6 Troubleshooting

| Problem | Solution |
|---|---|
| "setup.sh not found" | Move to the folder where the tool is saved, then run `./setup.sh`. |
| "command not found: ./setup.sh" | Run `chmod +x setup.sh` first. |
| "video file not found" | Check that the path to your video file is correct. |
| "existing transcription file not found" | Check that the path to your transcript file is correct. |
| "Model file not found" | Run `./setup.sh` to download the local AI model. |
| "llama-server was not found" | Run `./setup.sh`, or set the `LLAMA_SERVER_BIN` environment variable. |
| "Local LLM request failed" | Make sure the local model file is valid. |
| Whisper downloads a model each time | This is normal. It is cached after the first download. |
| FFmpeg is not found | Install FFmpeg (see Section 4). |

## 7 Testing

To run the automated tests, use:

```bash
venv/bin/python -m unittest discover -s tests -v
```

The tests check the comparison logic, the output files, and the command-line
flow.
