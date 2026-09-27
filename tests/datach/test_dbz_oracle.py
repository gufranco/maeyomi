"""Datach Dragon Ball Z's decoder against the game itself.

`tests/fixtures/oracle/datach_dbz.json` records what the game showed for 236
codes in MAME: the 36 official cards and 200 seeded random codes. The file
names the ROM digest and the emulator version it was recorded with.
"""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.dbz import DbzKind, decode_dbz

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "datach_dbz.json"


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


def accepted() -> list[dict[str, object]]:
    return [entry for entry in recorded() if entry["accepted"]]


@pytest.mark.parametrize("entry", accepted(), ids=lambda entry: str(entry["barcode"]))
def test_every_card_the_game_read_decodes_to_what_it_showed(entry: dict[str, object]) -> None:
    card = decode_dbz(str(entry["barcode"]))

    if card.kind is DbzKind.ITEM:
        assert card.character == entry["character"]
    else:
        assert (card.character, card.level, card.hp, card.bp, card.dp) == (
            entry["character"],
            entry["level"],
            entry["hp"],
            entry["bp"],
            entry["dp"],
        )


def test_the_record_is_large_enough_to_be_evidence() -> None:
    assert len(accepted()) >= 230


def test_every_official_card_was_read_by_the_game() -> None:
    official = [entry for entry in recorded() if "official_name" in entry]

    assert len(official) == 36
    assert all(entry["accepted"] for entry in official)


def test_the_codes_the_game_refused_under_emulation_are_kept_visible() -> None:
    refused = sorted(str(entry["barcode"]) for entry in recorded() if not entry["accepted"])

    assert refused == ["20158231", "3623401959035", "5532403373177", "6312422195214"]
