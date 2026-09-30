"""Tests for the cheat cards every machine and game offers, one or more kinds each."""

import pytest

from maeyomi.cheat_kinds import cheat_kind, cheat_kinds
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.device import Device
from maeyomi.registry import readable_as
from maeyomi.said import in_japanese

NAME = "Tester"
NUMBERLESS = frozenset({Device.DATACH_JLEAGUE})
"""Games whose cards carry nothing to raise: a J.League card names a player and no more."""
WITH_CHEATS = [device for device in Device if device not in NUMBERLESS]


@pytest.mark.parametrize("device", WITH_CHEATS, ids=str)
def test_every_device_offers_a_cheat_kind(device: Device) -> None:
    kinds = cheat_kinds(device)

    assert len(kinds) >= 1
    assert len({kind.key for kind in kinds}) == len(kinds)


@pytest.mark.parametrize("device", WITH_CHEATS, ids=str)
def test_every_cheat_card_is_read_by_its_device(device: Device) -> None:
    cards = [card for kind in cheat_kinds(device) for card in kind.cards(NAME)]

    unread = [card.barcode for card in cards if readable_as(device, card.barcode) is None]

    assert cards
    assert unread == []


@pytest.mark.parametrize("device", list(Device), ids=str)
def test_every_cheat_kind_is_named_in_both_languages(device: Device) -> None:
    for kind in cheat_kinds(device):
        assert kind.english.isascii()
        assert not kind.japanese.isascii()


def test_the_first_kind_is_the_default() -> None:
    assert cheat_kind(Device.BB2, None) == cheat_kinds(Device.BB2)[0]


def test_the_barcode_battler_ii_offers_a_warrior_its_items_fit() -> None:
    (card,) = cheat_kind(Device.BB2, "warrior").cards(NAME)

    assert isinstance(card.character, BarcodeBattlerCharacter)
    assert card.character.character_class is CharacterClass.WARRIOR
    assert card.character.hp == 99900


def test_the_barcode_battler_ii_items_are_five_cards() -> None:
    assert len(cheat_kind(Device.BB2, "items").cards(NAME)) == 5


def test_the_printed_name_is_the_one_asked_for() -> None:
    (card,) = cheat_kind(Device.BB2, "fighter").cards(NAME)

    assert card.name == NAME


def test_an_unknown_kind_names_the_kinds_there_are() -> None:
    with pytest.raises(ValueError, match="fighter, warrior, items") as raised:
        cheat_kind(Device.BB2, "ninja")

    assert in_japanese(raised.value.args[0])


@pytest.mark.parametrize("device", sorted(NUMBERLESS), ids=str)
def test_a_game_whose_cards_carry_no_numbers_says_so(device: Device) -> None:
    with pytest.raises(ValueError, match="carry no numbers") as raised:
        cheat_kind(device, None)

    assert in_japanese(raised.value.args[0])
