"""Tests for the reading, building and naming every Beena stripe game shares."""

from typing import Final

import pytest

from maeyomi.beena.stripe_game import StripeCard, StripeGame
from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.said import Said, in_japanese

ANY: Final = Constraint.anything()
GAME: Final = StripeGame(
    device=Device.DENSHA,
    title=("Sample", "サンプル"),
    cards=(
        StripeCard(1, "101000110011", ("Apple", "りんご"), ("Word card", "ことばの カード")),
        StripeCard(4, "100010110011", ("D", "ディー"), ("Letter card", "アルファベットの カード")),
    ),
    unknown=Said("no Sample card carries these bars", "サンプルに この バーの カードは ない"),
)


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


def test_a_code_is_matched_to_the_number_of_its_card() -> None:
    assert (GAME.match(" 100010110011 "), GAME.match("100000000011")) == (4, None)


def test_a_listed_code_reads_as_its_card() -> None:
    card = GAME.decode("100010110011")

    assert (card.ident, card.kind, card.game) == (1, GameKind.ITEM, Device.DENSHA)


def test_a_code_no_card_carries_is_refused_in_both_languages() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no Sample card") as raised:
        GAME.decode("100000000011")

    assert in_japanese(raised.value.args[0])


def test_the_card_asked_for_is_built_and_the_first_when_none_is() -> None:
    first = GAME.build(order(None))
    second = GAME.build(order(1))

    assert first is not None
    assert second is not None
    assert (first.ident, second.barcode) == (0, "100010110011")


def test_a_place_past_the_list_builds_nothing() -> None:
    assert GAME.build(order(2)) is None


def test_every_card_is_listed_with_its_name() -> None:
    assert [(entry.english, entry.japanese) for entry in GAME.entries()] == [
        ("Apple", "りんご"),
        ("D", "ディー"),
    ]


@pytest.mark.parametrize("typed", ["4", "100010110011", "04", "d", "ディー"])
def test_a_card_is_found_by_code_number_or_name(typed: str) -> None:
    assert GAME.named(typed) == 1


def test_a_typed_number_is_the_number_printed_on_the_card_not_its_place() -> None:
    assert (GAME.named("1"), GAME.named("01")) == (0, 0)


@pytest.mark.parametrize("typed", ["4", "04", "004", " 4 "])
def test_a_card_is_read_by_the_number_printed_on_it(typed: str) -> None:
    card = GAME.decode(typed)

    assert (card.ident, card.barcode) == (1, "100010110011")


def test_a_number_no_card_carries_is_refused_as_an_unknown_card() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no Sample card"):
        GAME.decode("7")


def test_a_name_no_card_has_is_refused() -> None:
    with pytest.raises(ValueError, match="no Sample card named"):
        GAME.named("Pikachu")


def test_a_card_says_its_name_kind_and_number() -> None:
    text = GAME.text(GAME.decode("100010110011"))

    assert (text.name, text.detail, text.power) == (
        ("D", "ディー"),
        ("Letter card", "アルファベットの カード"),
        ("04", "04"),
    )


def test_a_place_the_game_ignores_can_be_either_way() -> None:
    loose = StripeGame(
        device=GAME.device,
        title=GAME.title,
        cards=GAME.cards,
        unknown=GAME.unknown,
        ignored=frozenset({1}),
    )

    assert (loose.match("110010110011"), loose.decode("110010110011").ident) == (4, 1)
    assert GAME.match("110010110011") is None
