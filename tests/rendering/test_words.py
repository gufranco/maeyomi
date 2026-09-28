"""Tests for setting a card's words in its language."""

import pytest

from maeyomi.rendering.labels import SPECIAL_POWER, Bilingual
from maeyomi.rendering.language import CardLanguage
from maeyomi.rendering.text import JAPANESE_FONT, LATIN_FONT
from maeyomi.rendering.words import AbilityPanel, ability_lines, power_header

EFFECT = Bilingual("Halves the opponent's health", "あいての たいりょくを はんぶんに する")


def test_both_languages_head_the_panel_with_the_number_once() -> None:
    header = power_header(29, CardLanguage.BOTH)

    assert header == Bilingual(f"{SPECIAL_POWER.english} 29", SPECIAL_POWER.japanese)


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        (CardLanguage.ENGLISH, f"{SPECIAL_POWER.english} 29"),
        (CardLanguage.JAPANESE, f"{SPECIAL_POWER.japanese} 29"),
    ],
)
def test_one_language_keeps_the_number_after_its_own_words(
    language: CardLanguage, expected: str
) -> None:
    assert power_header(29, language) == Bilingual(expected, expected)


def test_both_languages_share_the_panel_english_first() -> None:
    lines = ability_lines(EFFECT, 60.0, 12.0, AbilityPanel(2.75, 6.5, CardLanguage.BOTH))

    assert [font for _, font in lines] == [LATIN_FONT, JAPANESE_FONT]


@pytest.mark.parametrize(
    ("language", "font"),
    [(CardLanguage.ENGLISH, LATIN_FONT), (CardLanguage.JAPANESE, JAPANESE_FONT)],
)
def test_one_language_fills_the_panel_alone(language: CardLanguage, font: str) -> None:
    lines = ability_lines(EFFECT, 20.0, 12.0, AbilityPanel(2.75, 6.5, language))

    assert lines
    assert {used for _, used in lines} == {font}
