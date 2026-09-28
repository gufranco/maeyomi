"""Tests for reading and building Datach Yu Yu Hakusho cards."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_reader import printable
from maeyomi.datach.yuyu import (
    LEVEL_KEY,
    MOVES_KEY,
    YuYuOrder,
    build_yuyu,
    codes_of,
    decode_yuyu,
    mask_of,
    picks_for,
    strongest_yuyu,
)
from maeyomi.decoder.errors import BarcodeError

FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "datach_yuyu.json"


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


@pytest.mark.parametrize("entry", recorded(), ids=lambda entry: str(entry["barcode"]))
def test_every_code_reads_as_the_game_itself_read_it_in_mame(entry: dict[str, object]) -> None:
    card = decode_yuyu(str(entry["barcode"]))

    assert (card.ident, mask_of(card)) == (entry["character"], entry["mask"])


def test_yusuke_carries_his_hp_sp_and_the_two_techniques_the_analyzer_listed() -> None:
    card = decode_yuyu("0871024742401")

    assert (card.kind, card.value("YHP"), card.value("YSP")) == (GameKind.FIGHTER, 3000, 2000)
    assert card.traits[1:] == (65, 67)


def test_an_item_adds_what_its_level_gives() -> None:
    card = decode_yuyu("0967652615603")

    assert (card.kind, card.ident, card.value("YHP")) == (GameKind.ITEM, 32, 500)


def test_an_item_that_changes_the_rules_carries_no_numbers() -> None:
    card = decode_yuyu("0946730251315")

    assert (card.ident, card.stats) == (39, ())


def test_the_secret_stream_is_the_hidden_toguro_at_9999() -> None:
    card = decode_yuyu("0882425300466")

    assert (card.kind, card.ident, card.value("YHP"), card.value("YSP")) == (
        GameKind.HIDDEN,
        20,
        9999,
        9999,
    )
    assert card.traits[1:] == (51, 52, 53, 65)


def test_a_malformed_code_is_refused_before_it_is_read() -> None:
    with pytest.raises(BarcodeError):
        decode_yuyu("0871024742400")


def test_a_fighter_is_built_with_the_techniques_picked() -> None:
    card = build_yuyu(YuYuOrder(0, ((MOVES_KEY, 0b1001),)))

    assert card is not None
    assert (card.ident, card.traits[1:]) == (0, (64, 66))
    assert printable(card.barcode)


def test_a_fighter_with_no_pick_gets_every_technique_it_has() -> None:
    card = build_yuyu(YuYuOrder(3))

    assert card is not None
    assert card.traits[1:] == (74, 73, 75)


def test_an_item_is_built_at_the_level_picked() -> None:
    card = build_yuyu(YuYuOrder(33, ((LEVEL_KEY, 3),)))

    assert card is not None
    assert card.value("YHP") == 1000


def test_the_hidden_character_is_built_from_its_secret() -> None:
    card = build_yuyu(YuYuOrder(20))

    assert card is not None
    assert card.kind is GameKind.HIDDEN


def test_any_card_is_a_fighter_when_none_is_named() -> None:
    card = build_yuyu(YuYuOrder(None))

    assert card is not None
    assert card.kind is GameKind.FIGHTER


def test_a_mask_a_fighter_cannot_use_builds_no_card() -> None:
    assert build_yuyu(YuYuOrder(0, ((MOVES_KEY, 16),))) is None


def test_a_fighter_offers_each_distinct_set_of_techniques_once() -> None:
    picks = picks_for(1)

    assert [pick.key for pick in picks] == [MOVES_KEY]
    assert [option.english for option in picks[0].options] == [
        "Spirit Sword, Extending Spirit Sword",
        "Spirit Sword",
        "Extending Spirit Sword",
        "No technique",
    ]


def test_an_item_that_adds_numbers_offers_its_levels() -> None:
    picks = picks_for(36)

    assert [option.english for option in picks[0].options] == [
        "Level 1: adds 100 HP and 50 SP",
        "Level 2: adds 200 HP and 70 SP",
        "Level 3: adds 300 HP and 90 SP",
        "Level 4: adds 400 HP and 110 SP",
    ]


def test_a_rule_item_and_the_hidden_character_offer_nothing() -> None:
    assert picks_for(38) == ()
    assert picks_for(20) == ()


def test_the_strongest_card_is_the_hidden_toguro() -> None:
    card = strongest_yuyu()

    assert (card.ident, card.value("YHP")) == (20, 9999)


def test_a_stream_no_digit_can_build_yields_no_code() -> None:
    assert list(codes_of(1)) == []
