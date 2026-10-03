import unittest

from animadex_ext.client import AnimaDexError, Character, parse_search_page
from animadex_ext.prompt import append_character


class SearchParsingTests(unittest.TestCase):
    def test_reads_documented_fields_and_preserves_tag_order(self):
        page = parse_search_page({
            "page": 2, "pages": 3, "total": 55,
            "results": [{
                "slug": "megumin", "name": "Megumin", "copyright_name": "KonoSuba",
                "trigger": "megumin, konosuba", "tags": ["1girl", "red eyes", "witch hat"],
                "thumb_url": "/thumb/characters/megumin?v=1",
            }],
        })
        self.assertEqual(page.page, 2)
        self.assertEqual(page.results[0].tags, ("1girl", "red eyes", "witch hat"))
        self.assertEqual(page.results[0].thumb_url, "https://animadex.net/thumb/characters/megumin?v=1")

    def test_missing_prompt_data_is_safe(self):
        page = parse_search_page({"results": [{"slug": "unknown"}]})
        self.assertEqual(page.results[0].trigger, "")
        self.assertEqual(page.results[0].tags, ())

    def test_rejects_wrong_search_shape(self):
        with self.assertRaises(AnimaDexError):
            parse_search_page({"results": {}})


class PromptImportTests(unittest.TestCase):
    def setUp(self):
        self.character = Character("megumin", "Megumin", "KonoSuba", "megumin, konosuba", ("1girl", "red eyes", "witch hat"), "")

    def test_trigger_only_appends_without_overwriting(self):
        self.assertEqual(append_character("masterpiece", self.character, False), "masterpiece, megumin, konosuba")

    def test_tags_preserve_order_and_skip_existing_terms(self):
        self.assertEqual(
            append_character("1girl, Megumin", self.character, True),
            "1girl, Megumin, konosuba, red eyes, witch hat",
        )

    def test_repeated_import_is_idempotent(self):
        once = append_character("", self.character, True)
        self.assertEqual(append_character(once, self.character, True), once)

    def test_missing_trigger_and_tags(self):
        empty = Character("x", "X", "", "", (), "")
        self.assertEqual(append_character("existing", empty, True), "existing")

    def test_tags_can_be_imported_without_a_trigger(self):
        tags_only = Character("x", "X", "", "", ("blue hair", "1girl"), "")
        self.assertEqual(append_character("", tags_only, False), "")
        self.assertEqual(append_character("", tags_only, True), "blue hair, 1girl")


if __name__ == "__main__":
    unittest.main()
