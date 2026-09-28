"""Tests for the shapes every game served through the dispatch table shares."""

from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import FIGHTING_KINDS, CardText, DatachGame, GameOrder
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

PAIR = ("x", "x")


def test_an_order_carries_no_choices_unless_given_some() -> None:
    order = GameOrder(1, (Constraint.anything(), Constraint.anything(), Constraint.anything()))

    assert order.picks == ()


def test_a_game_offers_no_picks_and_draws_fighting_cards_unless_told_otherwise() -> None:
    game = DatachGame(
        decode=lambda code: DatachCard(code, Device.LUPIN, GameKind.NO_EFFECT, 0),
        build=lambda _: None,
        strongest=None,
        entries=tuple,
        describe=lambda _: CardText(PAIR, PAIR, PAIR, PAIR),
        named=int,
        stat_keys=(),
    )

    assert (game.picks(0), game.drawable) == ((), FIGHTING_KINDS)
    assert GameKind.FIGHTER in game.drawable
