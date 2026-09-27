"""Tests that a card is written in the order a person would read it.

ReportLab emits no structure tree, so the order the text is drawn in is the
only reading order a screen reader or a text extractor can find. That makes
the drawing order a contract rather than an implementation detail: drawing the
barcode first, as an earlier version did, made every card open with thirteen
digits before its own name.
"""

from pathlib import Path

import pypdfium2 as pdfium
import pytest

from maeyomi.decoder.decode import decode
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.rendering.sheet import write_sheet

BARCODE = "4902102072618"
NAME = "Bottle of tea"


FIGHTER_BARCODE = "9994699095182"
FIGHTER_NAME = "Maximus"


def spoken_text(path: Path, name: str, barcode: str) -> str:
    write_sheet(
        [GeneratedCard(name=name, barcode=barcode, character=decode(barcode))],
        path,
        cut_marks=False,
        calibration=False,
    )
    document = pdfium.PdfDocument(str(path))
    try:
        return str(document[0].get_textpage().get_text_range())
    finally:
        document.close()


@pytest.fixture(name="spoken")
def spoken_fixture(tmp_path: Path) -> str:
    return spoken_text(tmp_path / "card.pdf", NAME, BARCODE)


@pytest.fixture(name="fighter")
def fighter_fixture(tmp_path: Path) -> str:
    return spoken_text(tmp_path / "fighter.pdf", FIGHTER_NAME, FIGHTER_BARCODE)


def test_the_card_opens_with_what_it_is_and_what_it_is_called(spoken: str) -> None:
    assert spoken.index("Armour") < spoken.index(NAME)


def test_the_name_comes_before_any_number(spoken: str) -> None:
    assert spoken.index(NAME) < spoken.index("DF")


def test_an_armour_card_announces_only_the_defence_it_carries(spoken: str) -> None:
    assert "HP" not in spoken.split("Special power", maxsplit=1)[0]
    assert "ST" not in spoken.split("Special power", maxsplit=1)[0]


def test_a_fighter_announces_its_numbers_in_card_order(fighter: str) -> None:
    assert fighter.index(FIGHTER_NAME) < fighter.index("HP") < fighter.index("ST")
    assert fighter.index("ST") < fighter.index("DF")


def test_the_special_power_is_read_before_the_barcode(spoken: str) -> None:
    assert spoken.index("Special power") < spoken.index("4 902102 072618")


def test_the_barcode_digits_are_real_text_a_reader_can_speak(spoken: str) -> None:
    assert "4 902102 072618" in spoken


def test_the_swipe_instruction_is_the_last_thing_on_the_card(spoken: str) -> None:
    assert spoken.index("4 902102 072618") < spoken.index("Swipe this end")


def test_both_languages_survive_extraction(spoken: str) -> None:
    assert "ぼうぐ" in spoken
    assert "ここを とおしてね" in spoken
