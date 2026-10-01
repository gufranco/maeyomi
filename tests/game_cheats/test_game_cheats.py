"""Tests for each game's cheat kinds: every kind reads, and a kind named for a number tops it."""

import random

import pytest

from maeyomi.datach.game_card import DatachCard
from maeyomi.datach.games import GAMES
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.game_cheats import CANDIDATES, GameCheat, game_cheats, later_numbers
from maeyomi.models.device import Device

SEED = 20260930
NUMBERLESS = frozenset({Device.DATACH_JLEAGUE, Device.CARD_DE_ASOBU})
SAMPLE = 3000
BODY = 12


def value_of(card: DatachCard, key: str) -> int:
    return max((stat.value for stat in card.stats if stat.key == key), default=0)


def sampled(device: Device) -> list[DatachCard]:
    rng = random.Random(SEED)  # noqa: S311
    cards: list[DatachCard] = []
    for _ in range(SAMPLE):
        body = "".join(str(rng.randrange(10)) for _ in range(BODY))
        try:
            cards.append(GAMES[device].decode(body + str(expected_check_digit(body))))
        except ValueError:
            continue
    return cards


def numbered() -> list[tuple[Device, GameCheat]]:
    return [
        (device, cheat)
        for device in GAMES
        for cheat in game_cheats(device)
        if cheat.stat is not None
    ]


@pytest.mark.parametrize("device", [d for d in GAMES if d not in NUMBERLESS], ids=str)
def test_every_game_offers_a_cheat(device: Device) -> None:
    cheats = game_cheats(device)

    assert cheats
    assert all(cheat.cards() for cheat in cheats)


@pytest.mark.parametrize("device", [d for d in GAMES if GAMES[d].strongest is not None], ids=str)
def test_the_first_kind_is_the_strongest_card(device: Device) -> None:
    strongest = GAMES[device].strongest

    assert strongest is not None
    assert game_cheats(device)[0].cards()[0].barcode == strongest().barcode


@pytest.mark.parametrize(("device", "cheat"), numbered(), ids=str)
def test_a_kind_named_for_a_number_has_the_most_of_it(device: Device, cheat: GameCheat) -> None:
    assert cheat.stat is not None
    best = max(value_of(card, cheat.stat) for card in cheat.cards())

    beaten = [card.barcode for card in sampled(device) if value_of(card, cheat.stat) > best]

    assert beaten == []


def test_a_game_with_several_ways_to_be_strongest_offers_each() -> None:
    keys = {device: [cheat.key for cheat in game_cheats(device)] for device in GAMES}

    assert keys[Device.BATTLE_SPACE] == ["strongest", "dp", "mp"]
    assert keys[Device.DATACH_SD_GUNDAM] == ["strongest", "hp", "ap", "dp"]
    assert keys[Device.FAMJOCK2][:3] == ["strongest", "mare", "stallion"]


@pytest.mark.parametrize(("key", "place"), [("ap", 3), ("mp", 2)])
def test_a_monster_maker_kind_gives_the_most_of_its_number_later(key: str, place: int) -> None:
    cheat = next(cheat for cheat in game_cheats(Device.MONSTER_MAKER) if cheat.key == key)
    (card,) = cheat.cards()

    every = [c for c in CANDIDATES[Device.MONSTER_MAKER]() if c is not None]

    assert later_numbers(card)[place] == max(later_numbers(c)[place] for c in every)
