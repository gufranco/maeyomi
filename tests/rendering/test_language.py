"""Tests for the languages a card can be printed in."""

from maeyomi.rendering.language import CardLanguage


def test_the_page_languages_are_the_card_languages_plus_both() -> None:
    assert [language.value for language in CardLanguage] == ["both", "en", "ja"]
