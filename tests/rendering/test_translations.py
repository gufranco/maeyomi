"""Tests for printing a card's words in one language."""

import pytest

from maeyomi.rendering.labels import Bilingual
from maeyomi.rendering.language import CardLanguage
from maeyomi.rendering.translations import catalogue, localise, template_of

ROBOT = Bilingual("Robot", "ロボット")
CHINESE = [CardLanguage.SIMPLIFIED, CardLanguage.HONG_KONG]


def test_both_languages_keep_the_text_as_it_is() -> None:
    assert localise(ROBOT, CardLanguage.BOTH) == ROBOT


@pytest.mark.parametrize(
    ("language", "expected"),
    [(CardLanguage.ENGLISH, "Robot"), (CardLanguage.JAPANESE, "ロボット")],
)
def test_one_language_prints_that_text_alone(language: CardLanguage, expected: str) -> None:
    assert localise(ROBOT, language) == Bilingual(expected, expected)


def test_numbers_become_placeholders_so_one_entry_serves_every_value() -> None:
    assert template_of("Fights with ST 24600") == ("Fights with ST {0}", ("24600",))


@pytest.mark.parametrize("language", CHINESE)
def test_chinese_puts_the_numbers_back_into_the_translation(language: CardLanguage) -> None:
    text = Bilingual("Fights with ST 24600", "たたかうと こうげき 24600。")

    printed = localise(text, language)

    assert printed.english == printed.japanese
    assert "24600" in printed.english
    assert printed.english != text.english


@pytest.mark.parametrize("language", CHINESE)
def test_a_proper_name_the_same_in_both_languages_is_left_alone(language: CardLanguage) -> None:
    name = Bilingual("がまもと くにくに", "がまもと くにくに")

    assert localise(name, language) == name


@pytest.mark.parametrize("language", CHINESE)
def test_a_joined_label_is_translated_part_by_part(language: CardLanguage) -> None:
    joined = Bilingual("Fights with ST 24600; No special power", "たたかうと のうりょく なし")

    printed = localise(joined, language).english

    assert "24600" in printed
    assert "Fights" not in printed
    assert "power" not in printed


@pytest.mark.parametrize("language", CHINESE)
def test_the_shared_catalogue_cannot_be_changed_by_a_caller(language: CardLanguage) -> None:
    words = catalogue(language)

    with pytest.raises(TypeError):
        words["Robot"] = "Robot"  # pyright: ignore[reportIndexIssue]


@pytest.mark.parametrize("language", CHINESE)
def test_text_the_catalogue_lacks_falls_back_to_english(language: CardLanguage) -> None:
    unknown = Bilingual("Zebra crossing 7", "しまうま 7")

    assert localise(unknown, language) == Bilingual("Zebra crossing 7", "Zebra crossing 7")
