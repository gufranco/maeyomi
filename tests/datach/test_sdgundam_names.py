"""Tests for the names Datach SD Gundam Wars gives its units, weapons and commands."""

import pytest

from maeyomi.datach.sdgundam_names import COMMANDS, UNITS, WEAPONS, card_named
from maeyomi.datach.sdgundam_tables import ARMS, BASES, FIRST_COMMAND, SLOTS


def test_every_unit_has_a_model_number_and_a_name_in_both_languages() -> None:
    assert set(UNITS) == set(range(len(BASES)))
    assert all(unit.model and unit.english and unit.japanese for unit in UNITS.values())


def test_every_weapon_a_unit_can_carry_is_named() -> None:
    carried = {weapon for arms in ARMS for pair in arms for weapon in pair}

    assert carried <= set(WEAPONS)


def test_every_command_a_slot_can_name_has_a_name_and_an_effect() -> None:
    reachable = {slot - FIRST_COMMAND + 1 for slot in SLOTS if slot >= FIRST_COMMAND}

    assert set(COMMANDS) == reachable
    assert all(command.effect and command.effect_japanese for command in COMMANDS.values())


@pytest.mark.parametrize(
    ("typed", "expected"),
    [("Gundam", 0), ("ガンダム", 0), ("RX-78", 0), ("13", 13), ("118", 118), ("White Base", 118)],
)
def test_a_card_is_found_by_either_name_its_model_or_its_number(typed: str, expected: int) -> None:
    assert card_named(typed) == expected


def test_an_unknown_card_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown SD Gundam Wars card"):
        card_named("Mazinger")
