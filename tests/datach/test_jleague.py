"""Tests for reading and building Datach J.League Super Top Players cards."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_reader import printable
from maeyomi.datach.jleague import build_jleague, codes_of, decode_jleague
from maeyomi.datach.jleague_names import ident_of
from maeyomi.decoder.errors import BarcodeError

FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "datach_jleague.json"


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


@pytest.mark.parametrize("entry", recorded(), ids=lambda entry: str(entry["barcode"]))
def test_every_code_reads_as_the_game_itself_read_it_in_mame(entry: dict[str, object]) -> None:
    card = decode_jleague(str(entry["barcode"]))

    team, number = divmod(card.ident, 16)
    kind = 1 if card.kind is GameKind.TEAM else entry["kind"]
    assert (kind, team) == (entry["kind"], entry["team"])
    if card.kind is GameKind.PLAYER:
        assert number == entry["player"]


def test_a_team_card_names_its_team_and_no_player() -> None:
    card = decode_jleague("1300400200000")

    assert (card.kind, card.ident) == (GameKind.TEAM, 0)


def test_a_player_card_names_the_team_and_the_slot() -> None:
    card = decode_jleague("1200520240125")

    assert (card.kind, card.ident) == (GameKind.PLAYER, ident_of(0, 1))


def test_a_malformed_code_is_refused_before_it_is_read() -> None:
    with pytest.raises(BarcodeError):
        decode_jleague("1200520240120")


@pytest.mark.parametrize("ident", [ident_of(3, 11), ident_of(9, 0), ident_of(7, 15)])
def test_a_card_is_built_for_the_team_or_player_asked_for(ident: int) -> None:
    card = build_jleague(ident)

    assert card is not None
    assert card.ident == ident
    assert printable(card.barcode)


def test_any_card_is_a_player_when_none_is_named() -> None:
    card = build_jleague(None)

    assert card is not None
    assert card.kind is GameKind.PLAYER


def test_a_card_the_game_does_not_have_builds_nothing() -> None:
    assert build_jleague(ident_of(10, 1)) is None


def test_a_stream_no_digit_can_build_yields_no_code() -> None:
    assert list(codes_of(1)) == []
