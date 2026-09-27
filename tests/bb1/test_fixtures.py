"""The first Barcode Battler's decoder against every card the wiki lists with values.

The fixtures are the four lists whose ability wording is the first device's:
the base set, チューハイカーンの逆襲, 最後の決戦ゴッドＶＳマザー and the candy
cards, fetched by `tools/fetch_bb1_fixtures.py` with each card's page recorded.
"""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.bb1.decode import decode_first
from maeyomi.decoder.errors import BarcodeError

FIXTURES: Final = Path(__file__).parent.parent / "fixtures" / "bb1_cards.json"
MISTYPED: Final = frozenset({"1444764195221"})
TRANSCRIPTION_SLIPS: Final[dict[str, str]] = {
    "0000007822001": "flag digits 00 listed as the check digit, 1",
    "0000400672005": "flag digits 00 listed as the check digit, 5",
    "0150000902009": "flag digits 00 listed as the check digit, 9",
    "0060000910105": "type digit 1 listed as 0",
    "0421813063004": "ST digits 18 listed as 4800",
}


def cards() -> list[dict[str, str | int | None]]:
    return json.loads(FIXTURES.read_text("utf-8"))["cards"]


def decoded_fields(card: FirstBattlerCard) -> dict[str, int | None]:
    return {
        "hp": card.hp,
        "st": card.st,
        "df": card.df,
        "dx": card.dx,
        "race": None if card.race is None else int(card.race),
        "job": card.job,
        "special": card.flag.code,
    }


def disagreements(entry: dict[str, str | int | None]) -> dict[str, tuple[object, object]]:
    got = decoded_fields(decode_first(str(entry["barcode"])))
    return {
        key: (got[key], entry[key])
        for key in got
        if entry[key] is not None and got[key] != entry[key]
    }


def usable() -> list[dict[str, str | int | None]]:
    excluded = MISTYPED | TRANSCRIPTION_SLIPS.keys()
    return [entry for entry in cards() if entry["barcode"] not in excluded]


@pytest.mark.parametrize("entry", usable(), ids=lambda entry: str(entry["barcode"]))
def test_every_listed_card_decodes_to_its_published_values(
    entry: dict[str, str | int | None],
) -> None:
    assert disagreements(entry) == {}


def test_the_fixtures_cover_all_four_lists() -> None:
    pages = {entry["source_page"] for entry in cards()}

    assert len(pages) == 4
    assert len(usable()) >= 110


@pytest.mark.parametrize("barcode", sorted(TRANSCRIPTION_SLIPS))
def test_each_excluded_slip_still_disagrees_on_exactly_one_field(barcode: str) -> None:
    entry = next(entry for entry in cards() if entry["barcode"] == barcode)

    assert len(disagreements(entry)) == 1


def test_the_mistyped_card_still_fails_its_own_check_digit() -> None:
    for barcode in MISTYPED:
        with pytest.raises(BarcodeError):
            decode_first(barcode)
