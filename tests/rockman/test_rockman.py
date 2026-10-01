"""Tests for Ryuusei no Rockman's Wave Card reading, as GBE+'s Wave Scanner notes describe it."""

from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.nds.rockman import (
    PRINTED,
    STAT_KEYS,
    build_rockman,
    decode_rockman,
    rockman_entries,
    rockman_named,
    rockman_text,
    sent,
)
from maeyomi.nds.rockman_tables import CARDS
from maeyomi.said import in_japanese

ANY: Final = Constraint.anything()
CANON: Final = "040000060019"


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


def test_the_scanner_sends_the_last_three_pairs_with_their_check_as_gbe_describes() -> None:
    assert sent("040000060019") == 0x40601333


def test_every_distinct_code_is_listed_once() -> None:
    assert len(PRINTED) == len({card.code for card in PRINTED}) == 211


def test_every_card_in_the_notes_is_reachable_by_its_code() -> None:
    assert {card[1] for card in CARDS} == {card.code for card in PRINTED}


def test_a_standard_card_is_named_and_numbered_as_the_notes_list_it() -> None:
    card = decode_rockman(CANON)

    text = rockman_text(card)

    assert card.kind is GameKind.ITEM
    assert text.name == ("Canon", "キャノン")
    assert text.detail == ("Standard card", "スタンダードカード")
    assert text.power == ("S-001", "S-001")


@pytest.mark.parametrize(
    ("code", "detail", "kind"),
    [
        ("040000063613", ("Giga card", "ギガカード"), GameKind.ITEM),
        ("040000240032", ("Character card", "キャラクターカード"), GameKind.FIGHTER),
    ],
)
def test_every_kind_of_card_says_what_it_is(
    code: str, detail: tuple[str, str], kind: GameKind
) -> None:
    card = decode_rockman(code)

    assert (rockman_text(card).detail, card.kind) == (detail, kind)


def test_a_mega_card_says_what_it_is() -> None:
    mega = next(card for card in PRINTED if card.number.startswith("M-"))

    assert rockman_text(decode_rockman(f"040000{mega.code}")).detail == ("Mega card", "メガカード")


def test_a_character_card_sharing_a_code_is_named_beside_the_card_it_matches() -> None:
    text = rockman_text(decode_rockman("040000060031"))

    assert text.name == ("Heavy Canon", "ヘビーキャノン")
    assert text.power == ("S-003, C-01 Rockman", "S-003、C-01 ロックマン")


def test_a_code_no_card_carries_is_refused_in_both_languages() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no Wave Card") as raised:
        decode_rockman("040000010101")

    assert in_japanese(raised.value.args[0])


@pytest.mark.parametrize("code", ["04000006001", "0400000600199", "04000006001A", "050000060019"])
def test_a_code_that_is_not_a_wave_card_barcode_is_refused(code: str) -> None:
    with pytest.raises(UnsupportedBarcodeError, match="040000"):
        decode_rockman(code)


def test_a_pair_the_scanner_cannot_send_is_refused() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="63"):
        decode_rockman("040000640000")


@pytest.mark.parametrize("ident", list(range(len(PRINTED))), ids=str)
def test_every_card_builds_and_reads_back_as_itself(ident: int) -> None:
    card = build_rockman(order(ident))

    assert card is not None
    assert decode_rockman(card.barcode).ident == ident


def test_the_first_card_is_built_when_none_is_named() -> None:
    card = build_rockman(order(None))

    assert card is not None
    assert card.ident == 0


def test_a_number_past_the_list_builds_nothing() -> None:
    assert build_rockman(order(len(PRINTED))) is None


def test_a_card_is_found_by_name_code_number_or_card_number() -> None:
    assert rockman_named(CANON) == 0
    assert rockman_named("0") == 0
    assert rockman_named("canon") == 0
    assert rockman_named("キャノン") == 0
    assert rockman_named("S-001") == 0
    with pytest.raises(ValueError, match="Wave Card"):
        rockman_named("Pikachu")


def test_every_entry_names_its_card_in_both_languages() -> None:
    entries = rockman_entries()

    assert len(entries) == len(PRINTED)
    assert all(entry.english.isascii() and entry.japanese for entry in entries)


def test_the_cards_carry_no_numbers() -> None:
    assert STAT_KEYS == ()
    assert decode_rockman(CANON).game is Device.ROCKMAN_DRAGON
