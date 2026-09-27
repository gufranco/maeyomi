"""Tests for the rule by which Datach Dragon Ball Z's reader accepts a barcode."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.dbz import decode_dbz
from maeyomi.datach.dbz_reader import (
    Readability,
    ReaderRefusalError,
    readability,
    width_classes,
)

FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "datach_dbz.json"


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


def test_a_code_is_measured_as_the_widths_of_its_bars_and_its_spaces() -> None:
    bars, spaces = width_classes("5532403373177")

    assert bars == frozenset({1, 2})
    assert spaces == frozenset({1, 2, 3, 4})


@pytest.mark.parametrize(
    ("barcode", "expected"),
    [
        ("0022248300117", Readability.READS),
        ("20158231", Readability.REFUSED),
        ("5532403373177", Readability.REFUSED),
        ("6312422195214", Readability.REFUSED),
        ("3623401959035", Readability.SPEED_DEPENDENT),
    ],
)
def test_the_reader_rule_classifies_each_code(barcode: str, expected: Readability) -> None:
    assert readability(barcode) is expected


def test_every_code_the_game_read_is_one_the_rule_lets_through() -> None:
    accepted = [str(entry["barcode"]) for entry in recorded() if entry["accepted"]]

    assert all(readability(code) is not Readability.REFUSED for code in accepted)


def test_every_code_the_game_refused_is_one_the_rule_flags() -> None:
    refused = [str(entry["barcode"]) for entry in recorded() if not entry["accepted"]]

    assert all(readability(code) is not Readability.READS for code in refused)


def test_a_refused_code_is_not_decoded_as_a_card() -> None:
    with pytest.raises(ReaderRefusalError, match="bars come in only 2 widths"):
        decode_dbz("5532403373177")


def test_a_code_that_reads_only_at_some_speeds_still_decodes() -> None:
    assert decode_dbz("3623401959035").barcode == "3623401959035"


def test_a_code_whose_spaces_have_only_two_widths_is_refused() -> None:
    with pytest.raises(ReaderRefusalError, match="spaces come in only 2 widths"):
        decode_dbz("6312422195214")
