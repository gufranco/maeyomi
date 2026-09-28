"""Tests for the games where a barcode sets off one effect from a fixed list."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.decoder.errors import BarcodeError
from maeyomi.games.alice import ALICE
from maeyomi.games.donald import DONALD
from maeyomi.games.effects import EffectGame, build_effect, decode_effect, strongest_effect
from maeyomi.games.lupin import LUPIN
from maeyomi.games.spiderman import SPIDERMAN
from maeyomi.models.device import Device

FIXTURES = Path(__file__).parent.parent / "fixtures" / "oracle"
GAMES = {"lupin": LUPIN, "donald": DONALD, "spiderman": SPIDERMAN, "alice": ALICE}
HP_HALF = 4


def recorded() -> list[tuple[str, str, int | None]]:
    return [
        (name, str(card["barcode"]), card["effect"])
        for name in GAMES
        for card in json.loads((FIXTURES / f"{name}.json").read_text("utf-8"))["cards"]
    ]


@pytest.mark.parametrize(("name", "barcode", "effect"), recorded())
def test_every_code_sets_off_what_the_game_did_in_mame(
    name: str, barcode: str, effect: int | None
) -> None:
    card = decode_effect(barcode, GAMES[name])

    expected = (GameKind.NO_EFFECT, None) if effect is None else (GameKind.EFFECT, effect)
    assert (card.kind, None if card.kind is GameKind.NO_EFFECT else card.ident) == expected


@pytest.mark.parametrize("name", GAMES)
def test_every_effect_the_game_lists_was_seen_in_mame(name: str) -> None:
    game = GAMES[name]
    seen = {effect for fixture, _, effect in recorded() if fixture == name}

    assert {effect.ident for effect in game.effects} == seen - {None}


@pytest.mark.parametrize("game", GAMES.values(), ids=list(GAMES))
def test_each_effect_is_built_as_a_code_that_sets_it_off(game: EffectGame) -> None:
    for effect in game.effects:
        card = build_effect(effect.ident, game)

        assert card is not None
        assert (card.kind, card.ident, card.game) == (GameKind.EFFECT, effect.ident, game.device)


@pytest.mark.parametrize("game", GAMES.values(), ids=list(GAMES))
def test_an_effect_the_game_does_not_have_builds_no_card(game: EffectGame) -> None:
    assert build_effect(99, game) is None


@pytest.mark.parametrize(
    ("game", "expected"), [(LUPIN, 0), (DONALD, 0), (SPIDERMAN, 1), (ALICE, 30)]
)
def test_the_cheat_is_the_effect_that_helps_the_player_most(
    game: EffectGame, expected: int
) -> None:
    assert strongest_effect(game).ident == expected


def test_a_short_code_is_read_with_the_five_zeros_the_interface_adds() -> None:
    card = decode_effect("10000007", SPIDERMAN)

    assert (card.kind, card.ident) == (GameKind.EFFECT, HP_HALF)


def test_the_cards_are_made_for_the_game_they_name() -> None:
    games = {game.device for game in GAMES.values()}

    assert games == {Device.LUPIN, Device.DONALD, Device.SPIDERMAN, Device.ALICE}


def test_a_malformed_code_is_refused_before_it_is_read() -> None:
    with pytest.raises(BarcodeError):
        decode_effect("4914177063570", LUPIN)
