import json
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from html.parser import HTMLParser
from pathlib import Path


THEME_ROOT = Path(__file__).resolve().parents[1]


class HeadParser(HTMLParser):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.links = []
        self.meta = {}
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag == "link" and attrs.get("rel") == "alternate":
            self.links.append(attrs)
        elif tag == "meta":
            self.meta[attrs.get("property", attrs.get("name"))] = attrs.get("content")


class MetadataParser(HTMLParser):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.lines = []
        self.current = None
        self.feed(html)

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        if tag == "div" and "meta-line" in attrs.get("class", "").split():
            self.current = {"text": "", "times": []}
        elif tag == "time" and self.current is not None:
            self.current["times"].append(attrs.get("datetime"))

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self.current is not None:
            self.current["text"] = " ".join(self.current["text"].split())
            self.lines.append(self.current)
            self.current = None


@unittest.skipUnless(shutil.which("zola"), "zola is required for template tests")
class ThemeTemplatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.directory = tempfile.TemporaryDirectory(prefix="nivis-template-tests-")
        cls.addClassCleanup(cls.directory.cleanup)
        cls.outputs = {}
        cls.example_config = tomllib.loads((THEME_ROOT / "config.toml").read_text(encoding="utf-8"))
        search_settings = "[search]\n" + "".join(
            f"{key} = {json.dumps(value)}\n" for key, value in cls.example_config["search"].items()
        )
        variants = {
            "both": 'generate_feeds = true\nfeed_filenames = ["rss.xml", "atom.xml"]',
            "default": "generate_feeds = true",
            "disabled": 'generate_feeds = false\nfeed_filenames = ["rss.xml", "atom.xml"]',
            "localized": (
                'generate_feeds = true\nfeed_filenames = ["rss.xml", "atom.xml"]\n'
                '[languages.fr]\ngenerate_feeds = false\n'
                'taxonomies = [{ name = "tags", paginate_by = 5 }]\n'
                '[languages.de]\ngenerate_feeds = true\nbuild_search_index = true\nfeed_filenames = ["atom.xml"]\n'
                'taxonomies = [{ name = "tags", paginate_by = 5 }]\n'
                '[languages.de.search]\nindex_format = "fuse_json"\n'
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
                'taxonomies = [{ name = "tags", paginate_by = 5 }]\n'
                f"build_search_index = {str(name == 'both').lower()}\n"
                f"{feeds}\n{search_settings}"
                '[extra]\nmath_display = "none"\nsocial_links = []\n'
                'taxonomy_mode = "category"\n'
                + ('content_lang = "zh-CN"\n' if name == "both" else "") +
                '[extra.sections]\nabout = false\narchive = false\n'
                'tags = true\nlinks = false\n',
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
                "same-day": "date = 2026-01-01\nupdated = 2026-01-01\n",
                "updated-only": "updated = 2026-02-03\n",
            }
            for slug, dates in pages.items():
                taxonomy = '\n[taxonomies]\ntags = ["Explorations"]\n' if slug == "revised" else ""
                (root / "content" / f"{slug}.md").write_text(
                    f'+++\ntitle = "{slug}"\n{dates}{taxonomy}+++\n## Heading\n\nBody.\n',
                    encoding="utf-8",
                )
            shutil.copyfile(root / "content" / "revised.md", root / "content" / "posts" / "revised.md")
            if name == "default":
                (root / "content" / "posts" / "revised.md").write_text(
                    '+++\ntitle = "French post"\ndate = 2026-01-01\n'
                    '[taxonomies]\ntags = ["Explorations"]\n'
                    '[extra]\ncontent_lang = "fr"\n+++\nBody.\n',
                    encoding="utf-8",
                )
            additional_pages = {
                "metadata-description": (
                    '+++\ntitle = \'A "quoted" & title\'\n'
                    'description = \' A "quote" & <em>emphasis</em>. \'\n'
                    '[extra]\nsubtitle = \'A "subtitle"\'\ncontent_lang = "en"\n'
                    'abstract = "This long abstract should not replace the description."\n'
                    '+++\nBody must not become the description.\n'
                ),
                "metadata-summary": '+++\ntitle = "Summary"\n+++\nA **bold** & "quoted" summary.\n\n<!-- more -->\n\nExcluded body.\n',
                "metadata-body": '+++\ntitle = "Body"\n+++\nBody **text** & "quotes".\n',
                "metadata-entities": '+++\ntitle = "Entities"\n+++\n`<tag>` and `&lt;` and `"quoted"`.\n',
                "metadata-long": '+++\ntitle = "Long"\ndescription = "' + '\u4e2d' * 150 + '"\n+++\n',
                "language-empty": '+++\ntitle = "Empty language"\n[extra]\ncontent_lang = ""\n+++\n',
                "search-full-text": (
                    '+++\ntitle = "Search fixture"\ndescription = "Search description"\n+++\n'
                    + ('\u4e2d\u6587\u6b63\u6587 ' * 300)
                    + '\n\nTail marker: Pohlig-Hellman.\n\n```text\nFENCED_CODE_ONLY\n```\n'
                ),
                "search-excluded": '+++\ntitle = "Excluded"\nin_search_index = false\n+++\nEXCLUDED_ONLY\n',
                "search-draft": '+++\ntitle = "Draft"\ndraft = true\n+++\nDRAFT_ONLY\n',
            }
            for slug, source in additional_pages.items():
                (root / "content" / f"{slug}.md").write_text(source, encoding="utf-8")
            if name == "localized":
                for language in ("fr", "de"):
                    for path in ("_index.md", "posts/_index.md", "revised.md"):
                        original = root / "content" / path
                        translated = original.with_name(f"{original.stem}.{language}.md")
                        shutil.copyfile(original, translated)
            result = subprocess.run(
                ["zola", "--root", str(root), "build"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode:
                raise AssertionError(result.stdout + result.stderr)
            cls.outputs[name] = root / "public"

    def head(self, variant: str, path: str = "index.html") -> HeadParser:
        return HeadParser((self.outputs[variant] / path).read_text(encoding="utf-8"))

    def test_example_exposes_language_and_an_opt_in_search_index(self) -> None:
        self.assertEqual(self.example_config["default_language"], "en")
        self.assertEqual(self.example_config["extra"]["content_lang"], "")
        self.assertFalse(self.example_config["build_search_index"])
        self.assertEqual(self.example_config["search"]["index_format"], "fuse_json")
        self.assertNotIn("truncate_content_length", self.example_config["search"])
        self.assertFalse(list(self.outputs["default"].glob("search_index.*")))

    def test_native_index_retains_full_body_and_respects_page_exclusions(self) -> None:
        index = json.loads((self.outputs["both"] / "search_index.en.json").read_text(encoding="utf-8"))
        item = next(item for item in index if item["url"].endswith("/search-full-text/"))
        self.assertEqual(item["title"], "Search fixture")
        self.assertEqual(item["description"], "Search description")
        self.assertIn('\u4e2d\u6587\u6b63\u6587', item["body"])
        self.assertGreater(item["body"].index("Pohlig-Hellman"), 1000)
        self.assertNotIn("FENCED_CODE_ONLY", item["body"])
        self.assertFalse(any(item["url"].endswith(("/search-excluded/", "/search-draft/")) for item in index))

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


    def metadata(self, path: str):
        return MetadataParser((self.outputs["both"] / path).read_text(encoding="utf-8")).lines

    def test_visible_update_is_between_creation_and_category_on_pages_and_lists(self) -> None:
        expected = {
            "text": "Jan. 01, 2026 / Updated Feb. 03, 2026 / Explorations",
            "times": ["2026-01-01", "2026-02-03"],
        }
        for path in ("revised/index.html", "posts/revised/index.html", "posts/index.html", "tags/explorations/index.html"):
            with self.subTest(path=path):
                lines = self.metadata(path)
                self.assertTrue(lines)
                self.assertTrue(all(line == expected for line in lines), lines)

    def test_missing_update_does_not_add_a_label_or_separator(self) -> None:
        self.assertEqual(self.metadata("original/index.html"), [{
            "text": "Jan. 01, 2026", "times": ["2026-01-01"],
        }])
        self.assertEqual(self.metadata("undated/index.html"), [{"text": "", "times": []}])

    def test_explicit_update_is_shown_even_on_the_publication_day(self) -> None:
        self.assertEqual(self.metadata("same-day/index.html"), [{
            "text": "Jan. 01, 2026 / Updated Jan. 01, 2026",
            "times": ["2026-01-01", "2026-01-01"],
        }])

    def test_update_without_creation_date_has_no_leading_separator(self) -> None:
        self.assertEqual(self.metadata("updated-only/index.html"), [{
            "text": "Updated Feb. 03, 2026", "times": ["2026-02-03"],
        }])

    def article_languages(self, variant: str, path: str):
        return [attrs.get("lang") for tag, attrs in self.head(variant, path).elements
                if tag == "article" and attrs.get("class") in ("content-article", "article-block")]

    def test_content_language_does_not_change_the_document_language(self) -> None:
        for path in ("revised/index.html", "posts/index.html", "tags/explorations/index.html"):
            with self.subTest(path=path):
                head = self.head("both", path)
                self.assertEqual(next(attrs["lang"] for tag, attrs in head.elements if tag == "html"), "en")
                self.assertTrue(self.article_languages("both", path))
                self.assertTrue(all(language == "zh-CN" for language in self.article_languages("both", path)))
        self.assertIn('xml:lang="en"', (self.outputs["both"] / "atom.xml").read_text(encoding="utf-8"))
        self.assertEqual(self.article_languages("both", "language-empty/index.html"), ["zh-CN"])

    def test_content_language_override_and_zola_fallback(self) -> None:
        self.assertEqual(self.article_languages("both", "metadata-description/index.html"), ["en"])
        self.assertEqual(self.article_languages("default", "revised/index.html"), ["en"])
        self.assertEqual(self.article_languages("localized", "fr/revised/index.html"), ["fr"])
        self.assertEqual(self.article_languages("localized", "de/revised/index.html"), ["de"])
        for path in ("posts/revised/index.html", "posts/index.html"):
            with self.subTest(path=path):
                self.assertEqual(self.article_languages("default", path), ["fr"])
        self.assertCountEqual(self.article_languages("default", "tags/explorations/index.html"), ["en", "fr"])

    def test_share_description_is_plain_text_and_attribute_safe(self) -> None:
        head = self.head("both", "metadata-description/index.html")
        self.assertEqual(head.meta["description"], 'A "quote" & emphasis.')
        self.assertEqual(head.meta["og:description"], head.meta["description"])
        self.assertEqual(head.meta["og:title"], 'A "quoted" & title\uff1aA "subtitle" | Test "feed" & site')
        self.assertEqual(head.meta["og:site_name"], 'Test "feed" & site')
        self.assertNotIn("og:image", head.meta)
        for tag, attrs in head.elements:
            if tag == "meta":
                self.assertTrue(set(attrs) <= {"property", "name", "content", "charset"}, attrs)

    def test_share_description_falls_back_to_summary_then_body(self) -> None:
        for slug, expected in (
            ("metadata-summary", 'A bold & "quoted" summary.'),
            ("metadata-body", 'Body text & "quotes".'),
            ("metadata-entities", '<tag> and &lt; and "quoted".'),
        ):
            with self.subTest(slug=slug):
                head = self.head("both", f"{slug}/index.html")
                self.assertEqual(head.meta["description"], expected)
                self.assertEqual(head.meta["og:description"], expected)
        long = self.head("both", "metadata-long/index.html").meta["og:description"]
        self.assertTrue(long.startswith('\u4e2d' * 90))
        self.assertLessEqual(len(long), 103)

    def test_topbar_uses_native_buttons_with_named_icons_on_regular_and_404_pages(self) -> None:
        for path in ("revised/index.html", "404.html"):
            with self.subTest(path=path):
                head = self.head("both", path)
                buttons = [attrs for tag, attrs in head.elements if tag == "button" and "icon-button" in attrs.get("class", "")]
                self.assertEqual(len(buttons), 7)
                self.assertTrue(all(button["type"] == "button" and button.get("aria-label") and button.get("title") for button in buttons))
                feed = next(button for button in buttons if button.get("aria-controls") == "feed-dropdown")
                self.assertEqual(feed["aria-expanded"], "false")
                panel = next(attrs for tag, attrs in head.elements if attrs.get("id") == "feed-dropdown")
                self.assertIn("hidden", panel)

    def test_visible_feed_links_follow_generation_and_language_settings(self) -> None:
        for variant, path, expected in (
            ("both", "revised/index.html", ["https://example.org/blog/rss.xml", "https://example.org/blog/atom.xml"]),
            ("default", "404.html", ["https://example.org/blog/atom.xml"]),
            ("disabled", "revised/index.html", []),
            ("disabled", "404.html", []),
            ("localized", "fr/revised/index.html", []),
            ("localized", "de/revised/index.html", ["https://example.org/blog/de/atom.xml"]),
        ):
            with self.subTest(variant=variant, path=path):
                head = self.head(variant, path)
                links = [attrs["href"] for tag, attrs in head.elements if tag == "a" and attrs.get("href", "").endswith(("/rss.xml", "/atom.xml"))]
                self.assertEqual(links, expected)
                self.assertEqual(any(attrs.get("aria-controls") == "feed-dropdown" for tag, attrs in head.elements), bool(expected))

    def test_search_switch_controls_markup_and_script_on_all_layouts(self) -> None:
        for path in ("index.html", "posts/index.html", "revised/index.html", "404.html"):
            for variant, enabled in (("both", True), ("default", False)):
                with self.subTest(path=path, variant=variant):
                    elements = self.head(variant, path).elements
                    controls = [attrs for tag, attrs in elements if attrs.get("id") == "search-toggle"]
                    scripts = [attrs for tag, attrs in elements if tag == "script" and "/search.js" in attrs.get("src", "")]
                    self.assertEqual(len(controls), int(enabled))
                    self.assertEqual(len(scripts), int(enabled))
                    if enabled:
                        self.assertEqual(controls[0]["aria-expanded"], "false")
                        self.assertEqual(scripts[0]["type"], "module")
                        search = next(attrs for tag, attrs in elements if "data-search-index" in attrs)
                        self.assertEqual(search["data-search-index"], "https://example.org/blog/search_index.en.json")
                        field = next(attrs for tag, attrs in elements if attrs.get("id") == "search-field")
                        self.assertIn("inert", field)

    def test_search_uses_zola_language_not_article_language(self) -> None:
        german = self.head("localized", "de/revised/index.html").elements
        search = next(attrs for tag, attrs in german if "data-search-index" in attrs)
        self.assertEqual(search["data-search-index"], "https://example.org/blog/search_index.de.json")
        self.assertTrue((self.outputs["localized"] / "search_index.de.json").exists())
        french = self.head("localized", "fr/revised/index.html").elements
        self.assertFalse(any("data-search-index" in attrs for tag, attrs in french))


if __name__ == "__main__":
    unittest.main()
