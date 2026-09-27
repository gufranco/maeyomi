"""Tests for which number tiles a card prints."""

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.generator.cheat_items import strongest_items
from maeyomi.rendering.stat_tiles import stat_tiles


def keys_and_values(barcode: str) -> list[tuple[str, int]]:
    return [(tile.key, tile.value) for tile in stat_tiles(decode(barcode))]


def test_a_fighter_prints_health_attack_and_defence() -> None:
    assert keys_and_values("9994699095182") == [("HP", 99900), ("ST", 14600), ("DF", 19900)]


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Cheat Blade", [("ST", 9900)]),
        ("Cheat Shield", [("DF", 9900)]),
        ("Cheat Potion", [("HP", 99900)]),
        ("Cheat Herbs", [("PP", 99)]),
        ("Cheat Crystal", [("MP", 99)]),
    ],
)
def test_an_item_prints_only_what_it_carries(name: str, expected: list[tuple[str, int]]) -> None:
    card = next(card for card in strongest_items() if card.name == name)

    assert keys_and_values(card.barcode) == expected


def test_an_information_item_prints_no_tile() -> None:
    assert keys_and_values("0000000950008") == []


def test_a_tile_is_coloured_by_the_number_it_is_filed_under() -> None:
    tiles = stat_tiles(decode("9994699095182"))

    assert [tile.style for tile in tiles] == ["HP", "ST", "DF"]
