#!/usr/bin/env python3
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

import transcribe_compare as tc


class DiffSegmentsTest(unittest.TestCase):
    def test_equal_text(self):
        segments = tc.diff_segments("hello world", "hello world")
        self.assertEqual(segments, [("equal", "hello world")])

    def test_insertion(self):
        segments = tc.diff_segments("hello world", "hello brave new world")
        kinds = [kind for kind, _ in segments]
        self.assertIn("insert", kinds)
        self.assertNotIn("delete", kinds)

    def test_deletion(self):
        segments = tc.diff_segments("hello brave new world", "hello world")
        kinds = [kind for kind, _ in segments]
        self.assertIn("delete", kinds)
        self.assertNotIn("insert", kinds)

    def test_replacement(self):
        segments = tc.diff_segments("hello cat", "hello dog")
        kinds = [kind for kind, _ in segments]
        self.assertIn("delete", kinds)
        self.assertIn("insert", kinds)


class RenderDiffsTest(unittest.TestCase):
    def test_render_insertion(self):
        segments = [("equal", "hello "), ("insert", "brave "), ("equal", "world")]
        self.assertEqual(tc.render_diffs(segments), "hello [+brave +]world")

    def test_render_deletion(self):
        segments = [("equal", "hello "), ("delete", "brave "), ("equal", "world")]
        self.assertEqual(tc.render_diffs(segments), "hello [-brave -]world")

    def test_render_equal_preserves_newlines(self):
        segments = [("equal", "line one\n"), ("equal", "line two")]
        self.assertEqual(tc.render_diffs(segments), "line one\nline two")


class BuildInlineDiffTest(unittest.TestCase):
    def test_identical_text_is_all_equal(self):
        segments = tc.build_inline_diff("a b c", "a b c")
        self.assertTrue(all(kind == "equal" for kind, _ in segments))
        self.assertEqual("".join(text for _, text in segments), "a b c")

    def test_changed_line_shows_inline_symbols(self):
        old = "line one\nhello cat\nline three"
        new = "line one\nhello dog\nline three"
        rendered = tc.render_diffs(tc.build_inline_diff(old, new))
        self.assertIn("[-cat-]", rendered)
        self.assertIn("[+dog+]", rendered)
        self.assertIn("line one", rendered)
        self.assertIn("line three", rendered)

    def test_added_line(self):
        old = "line one\nline three"
        new = "line one\nline two\nline three"
        rendered = tc.render_diffs(tc.build_inline_diff(old, new))
        self.assertIn("[+line two+]", rendered)

    def test_removed_line(self):
        old = "line one\nline two\nline three"
        new = "line one\nline three"
        rendered = tc.render_diffs(tc.build_inline_diff(old, new))
        self.assertIn("[-line two-]", rendered)

    def test_word_editor_style_on_transcript(self):
        old = "the quick brown fox jumps over the lazy dog"
        new = "the quick red fox leaps over the sleepy dog"
        rendered = tc.render_diffs(tc.build_inline_diff(old, new))
        self.assertEqual(
            rendered,
            "the quick [-brown-][+red+] fox [-jumps-][+leaps+] "
            "over the [-lazy-][+sleepy+] dog",
        )
        self.assertIn("the quick", rendered)


class ShowDiffsTest(unittest.TestCase):
    def test_no_differences(self):
        buffer = io.StringIO()
        with mock.patch("sys.stdout", buffer):
            tc.show_diffs("same text", "same text")
        self.assertIn("No differences found.", buffer.getvalue())

    def test_inline_default_includes_legend_and_symbols(self):
        buffer = io.StringIO()
        with mock.patch("sys.stdout", buffer):
            tc.show_diffs("hello cat", "hello dog")
        output = buffer.getvalue()
        self.assertIn("--- Differences ---", output)
        self.assertIn("Legend:", output)
        self.assertIn("[-cat-]", output)
        self.assertIn("[+dog+]", output)

    def test_classic_style(self):
        buffer = io.StringIO()
        with mock.patch("sys.stdout", buffer):
            tc.show_diffs("hello cat", "hello dog", diff_style="classic")
        output = buffer.getvalue()
        self.assertIn("--- Differences ---", output)
        self.assertNotIn("Legend:", output)


class FileIOTest(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.txt")
            tc.save_transcription("hello world", path)
            self.assertEqual(tc.load_transcription(path), "hello world")


class CliTest(unittest.TestCase):
    def test_cli_end_to_end_with_mocked_transcription(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = os.path.join(tmp, "lecture.mp4")
            existing = os.path.join(tmp, "expected.txt")
            output = os.path.join(tmp, "actual.txt")
            with open(video, "w") as f:
                f.write("dummy video")
            with open(existing, "w") as f:
                f.write("hello cat\nline two")
            with mock.patch(
                "transcribe_compare.transcribe_video", return_value="hello dog\nline two"
            ):
                buffer = io.StringIO()
                with mock.patch("sys.stdout", buffer):
                    with mock.patch(
                        "sys.argv",
                        [
                            "transcribe_compare.py",
                            video,
                            existing,
                            "-o",
                            output,
                            "--diff-style",
                            "inline",
                        ],
                    ):
                        tc.main()
            output_text = buffer.getvalue()
            self.assertIn("New transcription saved to:", output_text)
            self.assertIn("Legend:", output_text)
            self.assertIn("[-cat-]", output_text)
            self.assertIn("[+dog+]", output_text)
            self.assertTrue(os.path.exists(output))
            with open(output) as f:
                self.assertEqual(f.read().strip(), "hello dog\nline two")

    def test_cli_missing_video_file(self):
        with mock.patch("sys.argv", ["transcribe_compare.py", "nope.mp4", "x.txt"]):
            with mock.patch("sys.stderr", new=io.StringIO()):
                with self.assertRaises(SystemExit) as ctx:
                    tc.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_cli_missing_transcription_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = os.path.join(tmp, "lecture.mp4")
            with open(video, "w") as f:
                f.write("dummy video")
            with mock.patch(
                "sys.argv", ["transcribe_compare.py", video, "missing.txt"]
            ):
                with mock.patch("sys.stderr", new=io.StringIO()):
                    with self.assertRaises(SystemExit) as ctx:
                        tc.main()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
