"""Tests for Mushiking's card reading, against what the game's own comparison said."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.nds.mushiking import (
    CARDS,
    STAT_KEYS,
    build_mushiking,
    decode_mushiking,
    match,
    mushiking_entries,
    mushiking_named,
    mushiking_text,
)
from maeyomi.nds.mushiking_tables import CODES
from maeyomi.said import in_japanese

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "mushiking.json"
RECORDED: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
ANY: Final = Constraint.anything()


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


@pytest.mark.parametrize("card", RECORDED, ids=lambda card: card["barcode"])
def test_every_recorded_code_matches_the_card_the_game_matched(card: dict[str, object]) -> None:
    expected = None if card["list"] == -1 else (card["list"], card["index"], card["variant"])

    assert match(str(card["barcode"])) == expected


def test_every_printed_card_is_one_the_game_matches_as_itself() -> None:
    recorded = {card["barcode"]: (card["list"], card["index"]) for card in RECORDED}

    assert all(recorded[card.code] == (card.group, card.index) for card in CARDS)


def test_every_reachable_card_is_listed() -> None:
    assert len(CARDS) == 535


def test_a_beetle_card_is_named_after_its_beetle() -> None:
    card = decode_mushiking("GRFCT20K03W02")

    text = mushiking_text(card)

    assert card.kind is GameKind.FIGHTER
    assert text.name == ("Girafanokogirikuwagata", "ギラファノコギリクワガタ")
    assert text.detail == ("Beetle card", "ムシカード")


def test_a_character_card_is_named_after_its_character() -> None:
    text = mushiking_text(decode_mushiking(CARDS[mushiking_named("ジョー")].code))

    assert text.name == ("Joo", "ジョー")
    assert text.detail == ("Partner card", "パートナーカード")


@pytest.mark.parametrize(
    ("group", "name", "kind"),
    [
        (3, ("Move card 1", "わざカード 1"), GameKind.ITEM),
        (4, ("License card 1", "ライセンスカード 1"), GameKind.EFFECT),
        (5, ("Extra card 1", "とくべつカード 1"), GameKind.EFFECT),
        (6, ("Extra card 4", "とくべつカード 4"), GameKind.EFFECT),
    ],
)
def test_every_unnamed_list_numbers_its_cards(
    group: int, name: tuple[str, str], kind: GameKind
) -> None:
    first = next(card for card in CARDS if card.group == group)

    read = decode_mushiking(first.code)

    assert (mushiking_text(read).name, read.kind) == (name, kind)


def test_a_suffix_the_game_reads_is_named_on_the_card() -> None:
    code = next(card.code for card in CARDS if card.code.endswith("FFF"))

    text = mushiking_text(decode_mushiking(code[:10] + "MKF"))

    assert text.power == ("Read as version MKF", "MKF の バージョンとして よむ")


def test_a_code_no_card_carries_is_refused_in_both_languages() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no Mushiking card") as raised:
        decode_mushiking("AAAAAAAAAAAAA")

    assert in_japanese(raised.value.args[0])


def test_a_code_of_the_wrong_length_is_refused() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="13 characters"):
        decode_mushiking("GRFCT20K03W0")


def test_a_character_code39_cannot_carry_is_refused() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="Code 39"):
        decode_mushiking("grfct20k03w02")


def test_a_card_reads_the_same_framed_by_its_start_and_stop() -> None:
    assert decode_mushiking("*GRFCT20K03W02*").ident == decode_mushiking("GRFCT20K03W02").ident


@pytest.mark.parametrize("ident", list(range(len(CARDS))), ids=str)
def test_every_card_builds_and_reads_back_as_itself(ident: int) -> None:
    card = build_mushiking(order(ident))

    assert card is not None
    assert decode_mushiking(card.barcode).ident == ident


def test_the_first_card_is_built_when_none_is_named() -> None:
    card = build_mushiking(order(None))

    assert card is not None
    assert card.ident == 0


def test_a_number_past_the_list_builds_nothing() -> None:
    assert build_mushiking(order(len(CARDS))) is None


def test_a_card_is_found_by_name_code_or_number() -> None:
    assert mushiking_named("GRFCT20K03W02") == 0
    assert mushiking_named("0") == 0
    assert mushiking_named("Move card 1") == next(
        card.ident for card in mushiking_entries() if card.english == "Move card 1"
    )
    with pytest.raises(ValueError, match="Mushiking"):
        mushiking_named("Pikachu")


def test_the_cards_carry_no_numbers() -> None:
    assert STAT_KEYS == ()
    assert decode_mushiking("GRFCT20K03W02").game is Device.MUSHIKING


def test_no_card_in_the_second_list_ends_in_the_wildcard() -> None:
    assert not any(code.endswith("FFF") for code in CODES[1])
