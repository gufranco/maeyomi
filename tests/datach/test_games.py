"""Tests for the table of Datach games every surface dispatches through."""

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.games import GAMES, GameOrder, game_for
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

ANY: Constraint = Constraint.anything()


def test_every_game_after_dragon_ball_z_has_an_entry() -> None:
    assert set(GAMES) == {device for device in Device if device.is_game} - {Device.DATACH_DBZ}


def test_a_machine_or_dragon_ball_z_has_no_entry() -> None:
    assert game_for(Device.BB2) is None
    assert game_for(Device.DATACH_DBZ) is None


def test_each_game_reads_what_it_builds() -> None:
    for device, game in GAMES.items():
        card = game.build(GameOrder(game.entries()[0].ident, (ANY, ANY, ANY)))

        assert card is not None, device
        assert game.decode(card.barcode) == card


def test_each_game_lists_its_cards_with_names_in_both_languages() -> None:
    for game in GAMES.values():
        entries = game.entries()

        assert entries
        assert all(entry.english and entry.japanese for entry in entries)


def test_each_game_describes_a_card_it_read() -> None:
    game = GAMES[Device.DATACH_ULTRAMAN]

    text = game.describe(game.decode("0315424322677"))

    assert text.name == ("Zoffy", "ゾフィー")
    assert text.detail == ("Fighter", "せんし")


def test_an_item_is_described_as_an_item() -> None:
    game = GAMES[Device.DATACH_ULTRAMAN]

    text = game.describe(game.decode("0416434374356"))

    assert text.detail == ("Item card", "アイテム カード")


def test_the_strongest_card_is_one_the_game_reads_back() -> None:
    game = GAMES[Device.DATACH_ULTRAMAN]

    card = game.strongest()

    assert card is not None
    assert game.decode(card.barcode) == card


@pytest.mark.parametrize(("typed", "expected"), [("Zoffy", 3), ("ゼットン", 8)])
def test_a_card_is_found_by_the_name_the_game_gives_it(typed: str, expected: int) -> None:
    assert GAMES[Device.DATACH_ULTRAMAN].named(typed) == expected


def test_a_kind_that_is_not_an_item_is_a_fighter_in_ultraman_club() -> None:
    kinds = {entry.kind for entry in GAMES[Device.DATACH_ULTRAMAN].entries()}

    assert kinds == {GameKind.FIGHTER, GameKind.ITEM}
