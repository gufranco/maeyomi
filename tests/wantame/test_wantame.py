"""Tests for Wantame Music Channel's card reading, against what the game's own checks said."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.nds.wantame import (
    PRINTED,
    STAT_KEYS,
    build_wantame,
    decode_wantame,
    match,
    wantame_entries,
    wantame_named,
    wantame_text,
)
from maeyomi.said import in_japanese

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "wantame.json"
RECORDED: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
ANY: Final = Constraint.anything()
CHIHUAHUA: Final = "011112884427"
TURNED_AWAY: Final = "012111818409"


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


@pytest.mark.parametrize("card", RECORDED, ids=lambda card: card["barcode"])
def test_every_recorded_code_matches_the_card_the_game_found(card: dict[str, object]) -> None:
    expected = None if card["kind"] == 0 else (card["kind"], card["index"])

    assert match(str(card["barcode"])) == expected


def test_the_game_checked_every_recorded_checksum_and_refused_every_wrong_one() -> None:
    assert all(card["checked"] and card["wrong_check_refused"] for card in RECORDED)


def test_every_printed_card_is_one_the_game_found() -> None:
    found = {card["barcode"] for card in RECORDED if card["kind"]}

    assert {card.code for card in PRINTED} <= found


def test_every_card_the_game_takes_is_listed() -> None:
    assert len(PRINTED) == 235


def test_a_dog_card_is_named_after_its_breed() -> None:
    card = decode_wantame(CHIHUAHUA)

    text = wantame_text(card)

    assert card.kind is GameKind.FIGHTER
    assert text.name == ("Chiwawa", "チワワ")
    assert text.detail == ("Dog card", "いぬの カード")
    assert text.heading == ("Card number", "カードばんごう")
    assert text.power == ("002", "002")


@pytest.mark.parametrize(
    ("japanese", "english", "kind"),
    [
        ("しばいぬ（くろ）", "Shibainu (Kuro)", GameKind.FIGHTER),
        ("カモフラ×カーゴ", "Kamofura x Kaago", GameKind.ITEM),
        ("ワン■タジスタ", "Wan Tajisuta", GameKind.ITEM),
        ("ゆらゆら金ぎょT", "Yurayurakingyo T", GameKind.ITEM),
        ("B系シルバークロス", "B Kei Shirubaakurosu", GameKind.ITEM),
        ("ゆらりんシャボン玉", "Yurarinshabondama", GameKind.EFFECT),
    ],
)
def test_a_name_with_a_sign_or_kanji_is_spelled_in_latin_letters(
    japanese: str, english: str, kind: GameKind
) -> None:
    ident = wantame_named(japanese)

    card = decode_wantame(PRINTED[ident].code)

    assert (wantame_text(card).name, card.kind) == ((english, japanese), kind)


@pytest.mark.parametrize(
    ("ident", "detail"),
    [
        (36, ("Outfit card", "ふくの カード")),
        (173, ("Accessory card", "アクセサリの カード")),
        (234, ("Effect card", "エフェクトの カード")),
    ],
)
def test_every_kind_of_card_says_what_it_is(ident: int, detail: tuple[str, str]) -> None:
    assert wantame_text(decode_wantame(PRINTED[ident].code)).detail == detail


def test_the_card_the_game_turns_away_is_refused_in_both_languages() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="gives nothing") as raised:
        decode_wantame(TURNED_AWAY)

    assert in_japanese(raised.value.args[0])


def test_a_code_no_card_carries_is_refused_in_both_languages() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no Wantame card") as raised:
        decode_wantame("011199999999")

    assert in_japanese(raised.value.args[0])


@pytest.mark.parametrize("code", ["01111288442", "0111128844271", "01111288442A"])
def test_a_code_that_is_not_twelve_digits_is_refused(code: str) -> None:
    with pytest.raises(UnsupportedBarcodeError, match="12 digits"):
        decode_wantame(code)


def test_a_card_reads_the_same_with_spaces_around_it() -> None:
    assert decode_wantame(f" {CHIHUAHUA} ").ident == decode_wantame(CHIHUAHUA).ident


@pytest.mark.parametrize("ident", list(range(len(PRINTED))), ids=str)
def test_every_card_builds_and_reads_back_as_itself(ident: int) -> None:
    card = build_wantame(order(ident))

    assert card is not None
    assert decode_wantame(card.barcode).ident == ident


def test_the_first_card_is_built_when_none_is_named() -> None:
    card = build_wantame(order(None))

    assert card is not None
    assert card.ident == 0


def test_a_number_past_the_list_builds_nothing() -> None:
    assert build_wantame(order(len(PRINTED))) is None


def test_a_card_is_found_by_name_code_or_number() -> None:
    assert wantame_named(CHIHUAHUA) == 0
    assert wantame_named("0") == 0
    assert wantame_named("chiwawa") == 0
    assert wantame_named("チワワ") == 0
    with pytest.raises(ValueError, match="Wantame"):
        wantame_named("Pikachu")


def test_every_entry_names_its_card_in_both_languages() -> None:
    entries = wantame_entries()

    assert len(entries) == len(PRINTED)
    assert all(entry.english.isascii() for entry in entries)


def test_the_cards_carry_no_numbers() -> None:
    assert STAT_KEYS == ()
    assert decode_wantame(CHIHUAHUA).game is Device.WANTAME
