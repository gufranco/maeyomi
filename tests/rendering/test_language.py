"""Tests for the languages a card can be printed in."""

import pytest

from maeyomi.rendering.language import CardLanguage


def test_the_page_languages_are_the_card_languages_plus_both() -> None:
    assert [language.value for language in CardLanguage] == [
        "both",
        "en",
        "ja",
        "zh-Hans",
        "zh-Hant-HK",
    ]


@pytest.mark.parametrize(
    ("language", "chinese"),
    [
        (CardLanguage.BOTH, False),
        (CardLanguage.ENGLISH, False),
        (CardLanguage.JAPANESE, False),
        (CardLanguage.SIMPLIFIED, True),
        (CardLanguage.HONG_KONG, True),
    ],
)
def test_only_the_two_chinese_languages_are_chinese(language: CardLanguage, chinese: bool) -> None:
    assert language.is_chinese is chinese
