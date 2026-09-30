"""Tests that every Monster Maker name the game prints has one English name."""

from maeyomi.gameboy.monstermaker_names import CHARACTER_ENGLISH, CLASS_ENGLISH
from maeyomi.gameboy.monstermaker_tables import CLASS_NAMES, NAMES


def test_each_list_pairs_one_english_name_with_each_japanese_one() -> None:
    assert (len(CHARACTER_ENGLISH), len(CLASS_ENGLISH)) == (len(NAMES), len(CLASS_NAMES))


def test_no_two_characters_share_an_english_name() -> None:
    assert len(set(CHARACTER_ENGLISH)) == len(CHARACTER_ENGLISH)
