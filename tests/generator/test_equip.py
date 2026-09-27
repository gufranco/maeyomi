"""Tests for which Barcode Battler II fighters can use which items."""

import pytest

from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.decode import decode
from maeyomi.generator.cheat import strongest_card
from maeyomi.generator.cheat_items import strongest_items
from maeyomi.generator.equip import can_equip, equipping_jobs
from maeyomi.models.character import BarcodeBattlerCharacter


def health_item(sub_type: int) -> BarcodeBattlerCharacter:
    body = f"01000009{sub_type}000"
    return decode(body + str(expected_check_digit(body)))


def item(name: str) -> BarcodeBattlerCharacter:
    return next(card.character for card in strongest_items() if card.name == name)


@pytest.mark.parametrize("name", ["Cheat Blade", "Cheat Shield"])
def test_a_type_zero_weapon_or_armour_fits_every_warrior_and_no_magician(name: str) -> None:
    assert equipping_jobs(item(name)) == (0, 1, 2, 3, 4, 5, 6)


def test_the_cheat_fighter_is_a_magician_who_cannot_hold_the_blade() -> None:
    fighter = strongest_card().character

    assert not can_equip(fighter.job, item("Cheat Blade"))


@pytest.mark.parametrize("name", ["Cheat Potion", "Cheat Herbs", "Cheat Crystal"])
def test_the_cheat_fighter_can_use_the_potion_the_herbs_and_the_crystal(name: str) -> None:
    fighter = strongest_card().character

    assert can_equip(fighter.job, item(name))


@pytest.mark.parametrize(
    ("job", "sub_type", "expected"),
    [(0, 1, True), (0, 2, False), (9, 4, True), (5, 1, False)],
)
def test_a_health_item_follows_the_published_table(job: int, sub_type: int, expected: bool) -> None:
    assert can_equip(job, health_item(sub_type)) is expected


@pytest.mark.parametrize(("job", "expected"), [(6, False), (7, True), (8, False), (9, True)])
def test_a_magic_item_of_sub_type_eight_fits_only_the_published_magicians(
    job: int, expected: bool
) -> None:
    assert can_equip(job, item("Cheat Crystal")) is expected


def test_herbs_fit_everyone() -> None:
    assert equipping_jobs(item("Cheat Herbs")) == tuple(range(10))


def test_a_fighter_is_not_an_item_anyone_equips() -> None:
    assert equipping_jobs(strongest_card().character) == ()
