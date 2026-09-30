"""Tests for printing a card's words in one language."""

import pytest

from maeyomi.rendering.labels import Bilingual
from maeyomi.rendering.language import CardLanguage
from maeyomi.rendering.translations import localise

ROBOT = Bilingual("Robot", "ロボット")


def test_both_languages_keep_the_text_as_it_is() -> None:
    assert localise(ROBOT, CardLanguage.BOTH) == ROBOT


@pytest.mark.parametrize(
    ("language", "expected"),
    [(CardLanguage.ENGLISH, "Robot"), (CardLanguage.JAPANESE, "ロボット")],
)
def test_one_language_prints_that_text_alone(language: CardLanguage, expected: str) -> None:
    assert localise(ROBOT, language) == Bilingual(expected, expected)
