"""Tests for the tables Datach SD Gundam Wars decodes with."""

from maeyomi.datach.sdgundam_tables import (
    AP_BONUS,
    ARMS,
    BASES,
    COMMAND_COSTS,
    CP_BONUS,
    DP_BONUS,
    FIRST_COMMAND,
    HP_BONUS,
    PERMUTATION,
    RANK_BONUS,
    SLOTS,
)


def test_the_permutation_places_forty_bits_and_folds_every_fourth_bit_into_one() -> None:
    assert len(PERMUTATION) == 40
    assert {PERMUTATION[index] for index in range(3, 40, 4)} == {0x47}


def test_every_slot_is_a_unit_with_a_record_or_a_command() -> None:
    units = {slot for slot in SLOTS if slot < FIRST_COMMAND}

    assert len(SLOTS) == 128
    assert units == set(range(len(BASES)))


def test_every_unit_has_two_short_and_two_long_range_weapons() -> None:
    assert len(ARMS) == len(BASES) == 63


def test_each_bonus_table_has_one_entry_per_value_its_field_can_hold() -> None:
    assert (len(HP_BONUS), len(AP_BONUS), len(DP_BONUS)) == (32, 32, 32)
    assert (len(RANK_BONUS), len(CP_BONUS)) == (8, 4)


def test_every_command_has_a_cost() -> None:
    assert len(COMMAND_COSTS) == 61
    assert COMMAND_COSTS[30] == 10
