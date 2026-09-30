"""Tests that every Family Jockey 2 bonus the game announces has its words in both languages."""

from maeyomi.gameboy.famjock2_names import BONUSES, KINDS, STATS
from maeyomi.gameboy.famjock2_tables import BOXES


def test_each_namco_box_has_a_bonus_in_both_languages() -> None:
    assert len(BONUSES) == len(BOXES)
    assert all(english and japanese for english, japanese in BONUSES)


def test_the_three_menus_and_six_stats_are_named() -> None:
    assert (len(KINDS), len(STATS)) == (3, 6)
