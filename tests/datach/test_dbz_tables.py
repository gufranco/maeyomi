"""Tests for the invariants the numbers read from Datach Dragon Ball Z must hold."""

from maeyomi.datach.dbz_tables import (
    ADDENDS,
    BASES,
    FIGHTER_SLOTS,
    FORMS,
    FORMS_BY_CHARACTER,
    ITEM_SLOTS,
    LEVELS,
    PERMUTATION,
)


def test_every_digit_bit_lands_on_its_own_stream_bit() -> None:
    positions = {(entry >> 4, entry & 15) for entry in PERMUTATION}

    assert len(PERMUTATION) == 40
    assert len(positions) == 40
    assert all(byte < 5 and bit < 8 for byte, bit in positions)


def test_both_slot_tables_share_out_exactly_sixty_slots() -> None:
    assert sum(count for _, count in FIGHTER_SLOTS) == 60
    assert sum(count for _, count in ITEM_SLOTS) == 60


def test_every_stat_table_has_one_entry_per_four_bit_value() -> None:
    assert len(BASES) == len(ADDENDS) == 16
    assert len(LEVELS) == 8


def test_every_form_threshold_is_reachable_by_the_rule() -> None:
    ceiling = max(BASES) + max(ADDENDS) + 50

    for hp, bp, dp, _ in FORMS:
        assert hp <= ceiling
        assert max(bp, dp) <= ceiling // 2


def test_every_character_with_forms_names_records_that_exist() -> None:
    for records in FORMS_BY_CHARACTER.values():
        assert all(0 <= record < len(FORMS) for record in records)
