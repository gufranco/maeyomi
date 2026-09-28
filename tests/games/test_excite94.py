"""Tests for the players and items J.League Excite Stage '94 reads."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.decoder.errors import BarcodeError
from maeyomi.games.excite94 import (
    FIRST_ITEM,
    KICK_SPEED,
    OVERALL,
    build_excite94_item,
    build_excite94_player,
    decode_excite94,
    pk_item,
    player_ident,
    strongest_excite94,
)
from maeyomi.games.excite94_players import PLAYERS

TOP = 253
FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "excite94.json"


def recorded() -> list[dict[str, int | str]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


@pytest.mark.parametrize("entry", recorded(), ids=lambda entry: str(entry["barcode"]))
def test_every_code_reads_as_the_game_itself_read_it_in_mame(entry: dict[str, int | str]) -> None:
    card = decode_excite94(str(entry["barcode"]))

    assert (card.ident, card.traits) == (entry["ident"], (entry["trait"],))


def test_a_check_digit_of_four_or_more_is_one_of_the_hidden_players() -> None:
    card = decode_excite94("4900000011005")

    assert (card.kind, card.ident) == (GameKind.PLAYER, player_ident(12, 12))
    assert PLAYERS[card.ident][0] == "がまもと くにくに"


def test_an_eighth_digit_of_six_or_more_makes_a_keeper() -> None:
    card = decode_excite94("4900000700008")

    assert card.traits[0] == 1


def test_a_check_digit_below_four_is_an_item_card() -> None:
    card = decode_excite94("0000000034111")

    assert (card.kind, card.ident, card.traits) == (GameKind.ITEM, FIRST_ITEM + KICK_SPEED, (104,))


def test_every_hidden_player_but_the_one_no_sum_reaches_can_be_built() -> None:
    built = [build_excite94_player(ident) for ident in PLAYERS]

    missing = [ident for ident, card in zip(PLAYERS, built, strict=True) if card is None]
    assert missing == [player_ident(12, 0)]
    assert all(
        card is None or card.ident == ident for ident, card in zip(PLAYERS, built, strict=True)
    )


def test_an_item_is_built_with_the_value_asked_for() -> None:
    card = build_excite94_item(OVERALL, TOP)

    assert card is not None
    assert (card.ident, card.traits) == (FIRST_ITEM + OVERALL, (TOP,))


def test_the_strongest_card_is_the_player_graded_a_at_everything() -> None:
    assert strongest_excite94().ident == player_ident(12, 12)


def test_a_malformed_code_is_refused() -> None:
    with pytest.raises(BarcodeError):
        decode_excite94("4900000011000")


def test_a_value_no_item_carries_builds_no_card() -> None:
    assert build_excite94_item(OVERALL, TOP + 1) is None


PK_FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "excite94_pk.json"


def pk_recorded() -> list[dict[str, int | str | None]]:
    return json.loads(PK_FIXTURE.read_text("utf-8"))["cards"]


PK_ITEMS = [entry for entry in pk_recorded() if entry["player"] is None]
PK_PLAYERS = [entry for entry in pk_recorded() if entry["player"] is not None]


@pytest.mark.parametrize("entry", PK_ITEMS, ids=lambda entry: str(entry["barcode"]))
def test_pk_mode_reads_every_item_code_as_the_game_did_in_mame(
    entry: dict[str, int | str | None],
) -> None:
    item = pk_item(str(entry["barcode"]))

    assert item == (entry["pk_item"], entry["level"])


@pytest.mark.parametrize("entry", PK_PLAYERS, ids=lambda entry: str(entry["barcode"]))
def test_pk_mode_reads_every_player_code_as_the_roster_screen_does(
    entry: dict[str, int | str | None],
) -> None:
    code = str(entry["barcode"])

    item = pk_item(code)

    assert (item, decode_excite94(code).ident) == (None, entry["player"])
