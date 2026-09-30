"""Tests that every Battle Space name the game prints has one English name."""

from maeyomi.gameboy.battlespace_names import CLASS_ENGLISH, SPECIAL_ENGLISH, SPELL_ENGLISH
from maeyomi.gameboy.battlespace_tables import CLASS_NAMES, SPECIAL_NAMES, SPELL_NAMES


def test_each_list_pairs_one_english_name_with_each_japanese_one() -> None:
    assert (len(CLASS_ENGLISH), len(SPELL_ENGLISH), len(SPECIAL_ENGLISH)) == (
        len(CLASS_NAMES),
        len(SPELL_NAMES),
        len(SPECIAL_NAMES),
    )


def test_no_two_classes_share_an_english_name() -> None:
    assert len(set(CLASS_ENGLISH)) == len(CLASS_ENGLISH)
