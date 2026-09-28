"""Tests for the tables Datach Yu Yu Hakusho decodes with."""

from maeyomi.datach.yuyu_tables import (
    ITEM_BONUSES,
    NUMBERS,
    PERMUTATION,
    SECRET_CHARACTER,
    TECHNIQUES,
    TYPE_SLOTS,
)


def test_the_permutation_places_forty_bits_and_folds_every_fourth_bit_into_one() -> None:
    assert len(PERMUTATION) == 40
    assert {PERMUTATION[index] for index in range(3, 40, 4)} == {0x47}


def test_the_type_slots_cover_every_six_bit_value_exactly_once() -> None:
    assert sum(count for _, count in TYPE_SLOTS) == 64


def test_the_hidden_character_is_named_by_no_slot() -> None:
    assert SECRET_CHARACTER not in {ident for ident, _ in TYPE_SLOTS}


def test_every_character_has_numbers_and_four_technique_slots() -> None:
    assert len(NUMBERS) == len(TECHNIQUES) == 23


def test_every_item_has_four_levels() -> None:
    assert all(len(levels) == 4 for levels in ITEM_BONUSES)
