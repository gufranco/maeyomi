"""Tests for Anpanman Card de Tanoshiku ABC's card reading, against what the game said in MAME."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.beena.anpanman import (
    PRINTED,
    STAT_KEYS,
    anpanman_text,
    decode_anpanman,
    match,
)
from maeyomi.models.device import Device

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "anpanman.json"
RECORDED: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
D: Final = "101101111011"


@pytest.mark.parametrize("card", RECORDED, ids=lambda card: card["barcode"])
def test_a_code_is_listed_exactly_when_the_game_read_it(card: dict[str, object]) -> None:
    assert (match(str(card["barcode"])) is not None) == card["read"]


def test_every_card_the_game_read_is_the_card_its_bars_name() -> None:
    read = [
        (match(str(card["barcode"])), int(card["index"]) + 1) for card in RECORDED if card["read"]
    ]

    assert all(named == taken for named, taken in read)


def test_a_cards_second_place_can_be_either_way() -> None:
    variant = D[:1] + ("0" if D[1] == "1" else "1") + D[2:]

    assert decode_anpanman(variant).ident == decode_anpanman(D).ident


def test_every_listed_card_was_recorded() -> None:
    recorded = {card["barcode"] for card in RECORDED}

    assert {card.code for card in PRINTED} <= recorded


def test_the_game_has_26_letters_24_words_and_a_test_card() -> None:
    details = [card.detail[0] for card in PRINTED]

    assert (details.count("Letter card"), details.count("Word card"), len(PRINTED)) == (26, 24, 51)


def test_a_letter_card_is_named_after_its_letter() -> None:
    text = anpanman_text(decode_anpanman(D))

    assert (text.name, text.detail, text.power) == (
        ("D", "ディー"),
        ("Letter card", "アルファベットの カード"),
        ("04", "04"),
    )


def test_a_word_card_is_named_after_its_word() -> None:
    assert anpanman_text(decode_anpanman(PRINTED[26].code)).name == ("Apple", "りんご")


def test_the_last_card_is_the_test_card() -> None:
    assert PRINTED[-1].name == ("Test card", "テストカード")


def test_the_cards_carry_no_numbers() -> None:
    assert STAT_KEYS == ()
    assert decode_anpanman(D).game is Device.ANPANMAN
