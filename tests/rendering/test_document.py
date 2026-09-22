"""Tests for what a PDF says about itself.

A reader that cannot see the page still opens the file, and the first thing it
announces comes from here. These assert the bytes rather than the call, because
a metadata call that silently writes nothing is exactly the failure worth
catching.
"""

from pathlib import Path

import pypdfium2 as pdfium
import pytest

from barcode_battler.decoder.decode import decode
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.rendering.document import AUTHOR, LANGUAGE, SUBJECT
from barcode_battler.rendering.sheet import write_sheet

BARCODE = "4902102072618"


@pytest.fixture(name="card")
def card_fixture() -> GeneratedCard:
    return GeneratedCard(name="Tea", barcode=BARCODE, character=decode(BARCODE))


def pdf_title(path: Path) -> str:
    document = pdfium.PdfDocument(str(path))
    try:
        return document.get_metadata_dict().get("Title", "")
    finally:
        document.close()


def written(cards: list[GeneratedCard], tmp_path: Path, **kwargs: object) -> bytes:
    path = tmp_path / "sheet.pdf"
    write_sheet(cards, path, **kwargs)  # pyright: ignore[reportArgumentType]
    return path.read_bytes()


def test_the_document_carries_a_spoken_title(card: GeneratedCard, tmp_path: Path) -> None:
    path = tmp_path / "sheet.pdf"
    write_sheet([card], path)

    title = pdf_title(path)

    assert title == "Barcode Battler II card: Tea"


def test_a_sheet_of_several_is_named_for_what_is_on_it(card: GeneratedCard, tmp_path: Path) -> None:
    path = tmp_path / "sheet.pdf"
    write_sheet([card] * 4, path)

    title = pdf_title(path)

    assert title == "Barcode Battler II cards: 4 to cut out"


def test_a_caller_can_name_the_sheet_itself(card: GeneratedCard, tmp_path: Path) -> None:
    path = tmp_path / "sheet.pdf"
    write_sheet([card], path, title="The official Candy set")

    title = pdf_title(path)

    assert title == "The official Candy set"


def test_the_reader_is_told_to_speak_the_title_rather_than_the_filename(
    card: GeneratedCard, tmp_path: Path
) -> None:
    raw = written([card], tmp_path)

    assert b"/DisplayDocTitle true" in raw


def test_the_document_declares_its_language(card: GeneratedCard, tmp_path: Path) -> None:
    raw = written([card], tmp_path)

    assert f"/Lang ({LANGUAGE})".encode() in raw


def test_the_document_says_who_made_it_and_what_it_is(card: GeneratedCard, tmp_path: Path) -> None:
    raw = written([card], tmp_path)

    assert f"/Author ({AUTHOR})".encode() in raw
    assert f"/Subject ({SUBJECT})".encode() in raw
