import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


THEME_ROOT = Path(__file__).resolve().parents[1]


class HeadParser(HTMLParser):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.links = []
        self.meta = {}
        self.feed(html)

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "alternate":
            self.links.append(attrs)
        elif tag == "meta" and "property" in attrs:
            self.meta[attrs["property"]] = attrs.get("content")


@unittest.skipUnless(shutil.which("zola"), "zola is required for template tests")
class ThemeTemplatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.directory = tempfile.TemporaryDirectory(prefix="nivis-template-tests-")
        cls.addClassCleanup(cls.directory.cleanup)
        cls.outputs = {}
        variants = {
            "both": 'generate_feeds = true\nfeed_filenames = ["rss.xml", "atom.xml"]',
            "default": "generate_feeds = true",
            "disabled": 'generate_feeds = false\nfeed_filenames = ["rss.xml", "atom.xml"]',
            "localized": (
                'generate_feeds = true\nfeed_filenames = ["rss.xml", "atom.xml"]\n'
                '[languages.fr]\ngenerate_feeds = false\n'
                '[languages.de]\ngenerate_feeds = true\nfeed_filenames = ["atom.xml"]'
            ),
        }
        for name, feeds in variants.items():
            root = Path(cls.directory.name) / name
            (root / "themes").mkdir(parents=True)
            (root / "themes" / "nivis").symlink_to(THEME_ROOT, target_is_directory=True)
            (root / "content" / "posts").mkdir(parents=True)
            (root / "config.toml").write_text(
                'base_url = "https://example.org/blog"\n'
                'title = \'Test "feed" & site\'\n'
                'theme = "nivis"\n'
                f"{feeds}\n"
                '[extra]\nmath_display = "none"\nsocial_links = []\n'
                '[extra.sections]\nabout = false\narchive = false\n'
                'tags = false\nlinks = false\n',
                encoding="utf-8",
            )
            (root / "content" / "_index.md").write_text(
                '+++\ntitle = "Home"\n+++\n', encoding="utf-8"
            )
            (root / "content" / "posts" / "_index.md").write_text(
                '+++\ntitle = "Posts"\nsort_by = "date"\npaginate_by = 5\n+++\n',
                encoding="utf-8",
            )
            pages = {
                "original": "date = 2026-01-01\n",
                "revised": "date = 2026-01-01\nupdated = 2026-02-03\n",
                "undated": "",
            }
            for slug, dates in pages.items():
                (root / "content" / f"{slug}.md").write_text(
                    f'+++\ntitle = "{slug}"\n{dates}+++\n## Heading\n\nBody.\n',
                    encoding="utf-8",
                )
            if name == "localized":
                for language in ("fr", "de"):
                    for path in ("_index.md", "posts/_index.md", "revised.md"):
                        original = root / "content" / path
                        translated = original.with_name(f"{original.stem}.{language}.md")
                        shutil.copyfile(original, translated)
            subprocess.run(
                ["zola", "--root", str(root), "build"],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            cls.outputs[name] = root / "public"

    def head(self, variant: str, path: str = "index.html") -> HeadParser:
        return HeadParser((self.outputs[variant] / path).read_text(encoding="utf-8"))

    def test_feed_links_match_generated_formats_and_base_path(self) -> None:
        expected = {
            ("application/rss+xml", "https://example.org/blog/rss.xml"),
            ("application/atom+xml", "https://example.org/blog/atom.xml"),
        }
        for path in ("index.html", "posts/index.html", "original/index.html"):
            with self.subTest(path=path):
                links = self.head("both", path).links
                self.assertEqual(len(links), 2)
                self.assertEqual({(link["type"], link["href"]) for link in links}, expected)
                self.assertTrue(all(link["title"] == 'Test "feed" & site' for link in links))
        self.assertTrue((self.outputs["both"] / "rss.xml").is_file())
        self.assertTrue((self.outputs["both"] / "atom.xml").is_file())

    def test_default_feed_does_not_advertise_rss(self) -> None:
        links = self.head("default").links
        self.assertEqual([link["type"] for link in links], ["application/atom+xml"])
        self.assertTrue((self.outputs["default"] / "atom.xml").is_file())
        self.assertFalse((self.outputs["default"] / "rss.xml").exists())

    def test_disabled_feeds_are_not_advertised(self) -> None:
        self.assertEqual(self.head("disabled").links, [])
        self.assertFalse((self.outputs["disabled"] / "atom.xml").exists())
        self.assertFalse((self.outputs["disabled"] / "rss.xml").exists())

    def test_localized_pages_follow_their_own_feed_configuration(self) -> None:
        self.assertEqual(self.head("localized", "fr/index.html").links, [])
        self.assertFalse((self.outputs["localized"] / "fr" / "atom.xml").exists())
        links = self.head("localized", "de/index.html").links
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["type"], "application/atom+xml")
        self.assertEqual(links[0]["href"], "https://example.org/blog/de/atom.xml")
        self.assertTrue((self.outputs["localized"] / "de" / "atom.xml").is_file())
        self.assertFalse((self.outputs["localized"] / "de" / "rss.xml").exists())

    def test_modified_time_uses_updated_without_changing_publication(self) -> None:
        meta = self.head("both", "revised/index.html").meta
        self.assertEqual(meta["article:published_time"], "2026-01-01")
        self.assertEqual(meta["article:modified_time"], "2026-02-03")

    def test_modified_time_falls_back_to_publication(self) -> None:
        meta = self.head("both", "original/index.html").meta
        self.assertEqual(meta["article:published_time"], "2026-01-01")
        self.assertEqual(meta["article:modified_time"], "2026-01-01")

    def test_undated_pages_do_not_invent_dates(self) -> None:
        meta = self.head("both", "undated/index.html").meta
        self.assertNotIn("article:published_time", meta)
        self.assertNotIn("article:modified_time", meta)


if __name__ == "__main__":
    unittest.main()
