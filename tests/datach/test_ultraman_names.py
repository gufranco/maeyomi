"""Tests for the names Datach Ultraman Club gives each type."""

import pytest

from maeyomi.datach.ultraman_names import NAMES, type_named
from maeyomi.datach.ultraman_tables import TYPE_SLOTS


def test_every_type_the_game_can_read_has_a_name_in_both_languages() -> None:
    types = {identifier for identifier, _ in TYPE_SLOTS}

    assert set(NAMES) == types
    assert all(english and japanese for english, japanese in NAMES.values())


@pytest.mark.parametrize(
    ("typed", "expected"),
    [("zoffy", 3), ("ゾフィー", 3), (" Ultraseven ", 2), ("40", 40), ("ナックルせいじん", 50)],
)
def test_a_type_is_found_by_either_name_or_by_its_number(typed: str, expected: int) -> None:
    assert type_named(typed) == expected


@pytest.mark.parametrize("typed", ["Godzilla", "31", "-1"])
def test_an_unknown_type_is_refused_with_the_known_ones_listed(typed: str) -> None:
    with pytest.raises(ValueError, match="unknown Ultraman Club type"):
        type_named(typed)
