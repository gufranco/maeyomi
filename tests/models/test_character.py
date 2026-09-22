"""Tests for the decoded character model."""

import dataclasses

import pytest

from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType
from maeyomi.models.special_ability import SpecialAbility


def build(**overrides: object) -> BarcodeBattlerCharacter:
    base = {
        "barcode": "0401207237501",
        "read_type": ReadType.FRONT,
        "race": Race.AQUATIC,
        "job": 3,
        "hp": 4000,
        "st": 1200,
        "df": 700,
        "speed": 7,
        "special": SpecialAbility.from_code(50),
    }
    return BarcodeBattlerCharacter(**(base | overrides))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("job", "expected"),
    [
        (0, CharacterClass.WARRIOR),
        (6, CharacterClass.WARRIOR),
        (7, CharacterClass.MAGICIAN),
        (9, CharacterClass.MAGICIAN),
    ],
)
def test_character_class_follows_the_job_digit(job: int, expected: CharacterClass) -> None:
    character = build(job=job)

    assert character.character_class is expected


def test_an_item_has_no_character_class() -> None:
    character = build(race=Race.WEAPON, hp=0, st=600, df=0, job=0)

    assert character.character_class is None


def test_the_model_is_immutable() -> None:
    character = build()

    with pytest.raises(dataclasses.FrozenInstanceError):
        character.hp = 9999  # type: ignore[misc]


def test_device_units_are_display_values_divided_by_one_hundred() -> None:
    character = build(hp=4000, st=1200, df=700)

    assert (character.hp_units, character.st_units, character.df_units) == (40, 12, 7)


def test_a_fighter_is_reported_as_a_fighter() -> None:
    character = build()

    assert character.is_fighter


def test_a_display_value_that_is_not_a_multiple_of_one_hundred_is_rejected() -> None:
    with pytest.raises(ValueError, match="multiple of 100"):
        build(hp=4050)
