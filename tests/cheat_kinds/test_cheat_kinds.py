"""Tests for the cheat cards every machine and game offers, one or more kinds each."""

import pytest

from maeyomi.cheat_kinds import ALL, cheat_cards, cheat_kind, cheat_kinds, kind_name
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.device import Device
from maeyomi.registry import readable_as
from maeyomi.said import in_japanese

NAME = "Tester"
NUMBERLESS = frozenset({Device.DATACH_JLEAGUE, Device.CARD_DE_ASOBU, Device.OSHARE_MAJO})
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


def test_every_kind_together_prints_each_card_once() -> None:
    cards = cheat_cards(Device.BB2, ALL, None)

    barcodes = [card.barcode for card in cards]
    assert len(barcodes) == len(set(barcodes)) == 7


def test_one_kind_prints_only_its_cards() -> None:
    assert len(cheat_cards(Device.BB2, "items", NAME)) == 5


def test_every_kind_together_names_each_card_after_its_kind() -> None:
    cards = cheat_cards(Device.BARDIGUN, ALL, None)

    assert [card.name for card in cards] == [
        "Maximus Cheatimus",
        "Most power",
        "Most smarts",
        "Most speed",
    ]


def test_one_kind_with_no_name_typed_is_named_after_its_kind() -> None:
    cards = cheat_cards(Device.BARDIGUN, "smarts", None)

    assert cards[0].name == "Most smarts"


def test_the_default_kind_keeps_the_cheat_name() -> None:
    assert kind_name(Device.BARDIGUN, cheat_kind(Device.BARDIGUN, None)) == "Maximus Cheatimus"


def test_a_name_for_every_kind_at_once_is_refused_in_both_languages() -> None:
    with pytest.raises(ValueError, match="one kind") as raised:
        cheat_cards(Device.BARDIGUN, ALL, NAME)

    assert in_japanese(raised.value.args[0])
