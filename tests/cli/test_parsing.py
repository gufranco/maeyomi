"""Tests for reading constraints off the command line."""

import pytest

from maeyomi.cli.parsing import parse_character_class, parse_constraint, parse_race
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


@pytest.mark.parametrize("text", [None, "", "   "])
def test_an_absent_value_constrains_nothing(text: str | None) -> None:
    assert parse_constraint(text) == Constraint.anything()


def test_a_bare_number_is_an_exact_value() -> None:
    assert parse_constraint("5000") == Constraint.exactly(5000)


def test_a_hyphenated_pair_is_a_range() -> None:
    assert parse_constraint("5000-6000") == Constraint.between(5000, 6000)


@pytest.mark.parametrize("text", [">=1500", "> 1500", ">1500", "1500-"])
def test_a_lower_bound_is_recognised(text: str) -> None:
    assert parse_constraint(text) == Constraint.at_least(1500)


@pytest.mark.parametrize("text", ["<=3000", "<3000", "-3000"])
def test_an_upper_bound_is_recognised(text: str) -> None:
    assert parse_constraint(text) == Constraint.at_most(3000)


@pytest.mark.parametrize("text", ["abc", "5000..6000", "-"])
def test_an_unreadable_value_is_rejected_with_examples(text: str) -> None:
    with pytest.raises(ValueError, match="5000-6000"):
        parse_constraint(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("human", Race.HUMAN),
        ("HUMAN", Race.HUMAN),
        ("single use weapon", Race.SINGLE_USE_WEAPON),
        ("single-use-armour", Race.SINGLE_USE_ARMOUR),
    ],
)
def test_a_race_is_parsed_by_name(text: str, expected: Race) -> None:
    assert parse_race(text) is expected


def test_an_absent_race_is_none() -> None:
    assert parse_race(None) is None


def test_an_unknown_race_lists_the_valid_names() -> None:
    with pytest.raises(ValueError, match="mechanical"):
        parse_race("dragon")


@pytest.mark.parametrize(
    ("text", "expected"),
    [("warrior", CharacterClass.WARRIOR), ("MAGICIAN", CharacterClass.MAGICIAN)],
)
def test_a_class_is_parsed_by_name(text: str, expected: CharacterClass) -> None:
    assert parse_character_class(text) is expected


def test_an_absent_class_is_none() -> None:
    assert parse_character_class(None) is None


def test_an_unknown_class_lists_the_valid_names() -> None:
    with pytest.raises(ValueError, match="warrior"):
        parse_character_class("paladin")
