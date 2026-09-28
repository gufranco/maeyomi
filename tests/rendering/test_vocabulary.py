"""Tests that every word a card can print has a Chinese translation."""

from typing import Final

import pytest

from maeyomi.rendering.labels import SWIPE, Bilingual
from maeyomi.rendering.language import CardLanguage
from maeyomi.rendering.translations import PART_SEPARATOR, PLACEHOLDER, catalogue, template_of
from maeyomi.rendering.vocabulary import printed_texts

TEXTS: Final = printed_texts()


def test_the_vocabulary_holds_the_fixed_labels_and_decoded_cards() -> None:
    assert SWIPE in TEXTS
    assert Bilingual("Robot", "ロボット") in TEXTS
    assert len(TEXTS) > 500


@pytest.mark.parametrize("language", [CardLanguage.SIMPLIFIED, CardLanguage.HONG_KONG])
def test_every_printed_text_has_a_translation(language: CardLanguage) -> None:
    translated = catalogue(language)

    missing = sorted(
        {
            template_of(part)[0]
            for text in TEXTS
            if text.english != text.japanese
            for part in text.english.split(PART_SEPARATOR)
        }
        - set(translated)
    )

    assert missing == []


@pytest.mark.parametrize("language", [CardLanguage.SIMPLIFIED, CardLanguage.HONG_KONG])
def test_every_translation_keeps_the_placeholders_of_its_english(language: CardLanguage) -> None:
    mismatched = [
        key
        for key, words in catalogue(language).items()
        if sorted(PLACEHOLDER.findall(key)) != sorted(PLACEHOLDER.findall(words))
    ]

    assert mismatched == []
