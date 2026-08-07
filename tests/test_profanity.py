import unittest

from services.profanity import (
    CensureLineResult,
    check_for_profanity,
    check_for_profanity_all,
    check_name_for_violations,
    find_profanity,
    normalize_text,
)


class ProfanityServiceTestCase(unittest.TestCase):
    def test_plain_profanity_is_detected(self):
        self.assertTrue(check_for_profanity("shit", "en").detected)
        self.assertTrue(check_for_profanity("хуй", "ru").detected)

    def test_unicode_compatibility_characters_are_normalized(self):
        result = check_for_profanity("ｓｈｉｔ", "en")
        self.assertTrue(result.detected)
        self.assertEqual(result.word, "shit")

    def test_invisible_format_characters_are_removed(self):
        self.assertEqual(normalize_text("sh\u200bit"), "shit")
        self.assertTrue(check_for_profanity("sh\u200bit", "en").detected)

    def test_short_fragments_cannot_bypass_detection(self):
        self.assertTrue(check_for_profanity("sh it", "en").detected)
        self.assertTrue(check_for_profanity("ху\u00a0й", "ru").detected)

    def test_clean_text_is_not_flagged(self):
        result = check_for_profanity("hello world", "en")
        self.assertFalse(result.detected)
        self.assertIsNone(result.word)
        self.assertIsInstance(result.line, CensureLineResult)

    def test_invalid_language_is_rejected(self):
        with self.assertRaises(ValueError):
            check_for_profanity("text", "typo")

    def test_all_languages_and_mixed_language_names(self):
        self.assertEqual(check_for_profanity_all("hello world"), (False, None))
        self.assertFalse(check_name_for_violations("John хуй"))

    def test_common_confusables_are_detected(self):
        self.assertTrue(check_for_profanity("sh1t", "en").detected)
        self.assertTrue(check_for_profanity("$hit", "en").detected)
        self.assertTrue(check_for_profanity("shіt", "en").detected)  # Cyrillic і

    def test_prefixed_russian_profanity_with_latin_confusables(self):
        text = "но всем поxyй извините я хочу проверить бота"
        result = check_for_profanity(text, "ru")
        self.assertTrue(result.detected)
        self.assertEqual(result.word, "поxyй")

    def test_call_specific_allowlist_suppresses_exact_words_only(self):
        self.assertFalse(
            check_for_profanity("shit", "en", allowlist={"shit"}).detected
        )
        self.assertTrue(
            check_for_profanity("shit bitch", "en", allowlist={"shit"}).detected
        )

    def test_structured_match_has_original_offsets_and_reason(self):
        text = "say sh\u200bit now"
        matches = find_profanity(text, languages=("en",))
        self.assertEqual(len(matches), 1)
        match = matches[0]
        self.assertEqual(match.text, "sh\u200bit")
        self.assertEqual(text[match.start:match.end], match.text)
        self.assertEqual(match.normalized, "shit")
        self.assertEqual(match.language, "en")
        self.assertEqual(match.reason, "word")
        self.assertIsNotNone(match.pattern)


if __name__ == "__main__":
    unittest.main()
