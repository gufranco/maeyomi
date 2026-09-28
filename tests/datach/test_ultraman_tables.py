"""Tests for the tables Datach Ultraman Club decodes with."""

from maeyomi.datach.ultraman_tables import ADDENDS, PERMUTATION, TENS, TYPE_SLOTS


def test_the_permutation_places_forty_bits_and_folds_every_fourth_bit_into_one() -> None:
    fourth_bits = {PERMUTATION[index] for index in range(3, 40, 4)}

    assert len(PERMUTATION) == 40
    assert fourth_bits == {0x47}


def test_every_hundreds_value_from_0_to_99_can_be_made_from_the_two_tables() -> None:
    reachable = {ten + addend for ten in TENS for addend in ADDENDS}

    assert reachable == set(range(100))


def test_the_type_slots_cover_every_six_bit_value_exactly_once() -> None:
    total = sum(count for _, count in TYPE_SLOTS)

    assert total == 64
