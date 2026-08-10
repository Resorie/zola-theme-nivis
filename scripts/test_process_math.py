import tempfile
import unittest
from pathlib import Path

from scripts.process_math import process_content, process_file, process_paths


def document(body: str) -> str:
    return f'+++\ntitle = "test"\n+++\n{body}'


class ProcessMathTest(unittest.TestCase):
    def test_encodes_punctuation_but_keeps_dollar_delimiters(self) -> None:
        source = document("Value $a_b<c*d$ and\n$$\n\\begin{aligned}\nx&=y\\\\\n\\end{aligned}\n$$\n")

        result = process_content(source)

        self.assertIn("$a&#95;b&#60;c&#42;d$", result)
        self.assertIn("$$\n&#92;begin&#123;aligned&#125;", result)
        self.assertIn("x&#38;&#61;y&#92;&#92;", result)
        self.assertNotIn('<div class="math-display">', result)

    def test_preserves_all_four_blank_line_relationships(self) -> None:
        body = (
            "tight-before\n$$x+y$$\ntight-after\n\n"
            "separate-before\n\n$$x+y$$\n\nseparate-after\n\n"
            "continue-before\n$$x+y$$\n\nafter-break\n\n"
            "before-break\n\n$$x+y$$\ncontinue-after\n"
        )

        result = process_content(document(body))

        self.assertIn("tight-before\n$$x&#43;y$$\ntight-after", result)
        self.assertIn("separate-before\n\n$$x&#43;y$$\n\nseparate-after", result)
        self.assertIn("continue-before\n$$x&#43;y$$\n\nafter-break", result)
        self.assertIn("before-break\n\n$$x&#43;y$$\ncontinue-after", result)

    def test_migrates_legacy_wrappers_without_changing_outer_whitespace(self) -> None:
        body = (
            "before\n"
            '<div class="math-display">$$a&amp;b&lt;c$$</div>\n'
            "after `$x_y$`\n"
            '> <div class="math-display">$$u&amp;v$$</div>\n'
        )

        restored = process_content(document(body), restore_only=True)
        processed = process_content(document(body))

        self.assertIn("before\n$$a&b<c$$\nafter $x_y$", restored)
        self.assertIn("> $$u&v$$", restored)
        self.assertIn("before\n$$a&#38;b&#60;c$$\nafter $x&#95;y$", processed)
        self.assertIn("> $$u&#38;v$$", processed)

    def test_leaves_fenced_and_non_math_inline_code_untouched(self) -> None:
        body = (
            "```cpp\n"
            'const char* formula = "$a_b$";\n'
            '<div class="math-display">$$x&y$$</div>\n'
            "```\n"
            "Use `$HOME` and $a_b$.\n"
        )

        result = process_content(document(body))

        self.assertIn('const char* formula = "$a_b$";', result)
        self.assertIn('<div class="math-display">$$x&y$$</div>', result)
        self.assertIn("`$HOME`", result)
        self.assertIn("$a&#95;b$", result)

    def test_is_idempotent(self) -> None:
        source = document("`$a_b$`\n<div class=\"math-display\">$$x&amp;y$$</div>\n")
        once = process_content(source)
        twice = process_content(once)
        self.assertEqual(once, twice)

    def test_check_mode_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "post.md"
            source = document("$a_b$\n")
            path.write_text(source, encoding="utf-8")

            changed = process_file(path, check=True)

            self.assertTrue(changed)
            self.assertEqual(source, path.read_text(encoding="utf-8"))

    def test_processes_every_file_without_short_circuiting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.md"
            second = root / "second.md"
            first.write_text(document("$a_b$\n"), encoding="utf-8")
            second.write_text(document("$x_y$\n"), encoding="utf-8")

            changed = process_paths([first, second])

            self.assertTrue(changed)
            self.assertIn("$a&#95;b$", first.read_text(encoding="utf-8"))
            self.assertIn("$x&#95;y$", second.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
