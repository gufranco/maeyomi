"""Tests for how the Datach games after Dragon Ball Z read a barcode's bars."""

import pytest

from maeyomi.datach.dbz_reader import Readability
from maeyomi.datach.game_reader import game_readability, printable


@pytest.mark.parametrize(
    ("barcode", "expected"),
    [
        ("0344046250372", Readability.READS),
        ("0315424322677", Readability.SPEED_DEPENDENT),
        ("5532403373177", Readability.READS),
        ("20158231", Readability.READS),
        ("3623401959035", Readability.SPEED_DEPENDENT),
        ("4291609032240", Readability.SPEED_DEPENDENT),
    ],
)
def test_only_a_code_with_widths_1_2_and_4_depends_on_the_swipe(
    barcode: str, expected: Readability
) -> None:
    assert game_readability(barcode) is expected


@pytest.mark.parametrize(
    ("barcode", "expected"),
    [("0344046250372", True), ("5532403373177", False), ("0315424322677", False)],
)
def test_a_made_card_uses_only_codes_every_datach_reader_accepts(
    barcode: str, expected: bool
) -> None:
    assert printable(barcode) is expected
