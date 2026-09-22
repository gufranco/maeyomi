"""Tests for writing a printable sheet of cards.

The assertion that matters is the last one in each case: every barcode on the
rendered page is rasterised and decoded, and must equal the code printed on
that card. A test on the digit string alone would pass on a sheet whose ink no
scanner can read.
"""

from pathlib import Path

import pypdfium2 as pdfium
import pytest

from barcode_battler.barcode.rasterise import render_pdf_pages
from barcode_battler.barcode.verify import decode_image, decode_pdf
from barcode_battler.generator.random_cards import generate_random
from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.constraint import Constraint
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.rendering.calibration import REFERENCE_LENGTH_MM
from barcode_battler.rendering.layout import SheetLayout
from barcode_battler.rendering.sheet import write_sheet


def cards(count: int) -> tuple[GeneratedCard, ...]:
    template = CardRequest(
        hp=Constraint.between(1000, 10000),
        st=Constraint.between(100, 3000),
        df=Constraint.between(100, 3000),
    )
    return generate_random(count, template=template, seed=42).cards


def test_a_sheet_is_written_and_reports_its_page_count(tmp_path: Path) -> None:
    path = tmp_path / "one.pdf"

    pages = write_sheet(cards(9), path)

    assert pages == 1
    assert path.exists()


def test_every_barcode_on_the_sheet_decodes_to_the_code_it_prints(tmp_path: Path) -> None:
    path = tmp_path / "nine.pdf"
    batch = cards(9)

    write_sheet(batch, path)

    assert sorted(decode_pdf(path)) == sorted(card.barcode for card in batch)


def test_a_batch_larger_than_one_page_spans_pages(tmp_path: Path) -> None:
    path = tmp_path / "many.pdf"
    batch = cards(24)

    pages = write_sheet(batch, path)

    assert pages == 3
    assert sorted(decode_pdf(path)) == sorted(card.barcode for card in batch)


def test_an_empty_batch_writes_no_pages(tmp_path: Path) -> None:
    path = tmp_path / "empty.pdf"

    assert write_sheet((), path) == 0
    assert not path.exists()


def test_a_custom_layout_is_honoured(tmp_path: Path) -> None:
    path = tmp_path / "two-up.pdf"
    layout = SheetLayout(card_width_mm=90.0, card_height_mm=130.0)
    batch = cards(2)

    pages = write_sheet(batch, path, layout=layout)

    assert layout.cards_per_page == 4
    assert pages == 1
    assert sorted(decode_pdf(path)) == sorted(card.barcode for card in batch)


def test_cut_marks_can_be_turned_off(tmp_path: Path) -> None:
    with_marks = tmp_path / "marks.pdf"
    without_marks = tmp_path / "plain.pdf"
    batch = cards(1)

    write_sheet(batch, with_marks, cut_marks=True)
    write_sheet(batch, without_marks, cut_marks=False)

    assert with_marks.stat().st_size != without_marks.stat().st_size
    assert decode_pdf(without_marks) == [batch[0].barcode]


def test_a_card_too_small_for_its_barcode_is_rejected(tmp_path: Path) -> None:
    layout = SheetLayout(card_width_mm=30.0, card_height_mm=40.0)

    with pytest.raises(ValueError, match="too narrow"):
        write_sheet(cards(1), tmp_path / "small.pdf", layout=layout)


def page_text(path: Path) -> str:
    document = pdfium.PdfDocument(str(path))
    try:
        return str(document[0].get_textpage().get_text_range())
    finally:
        document.close()


def test_a_sheet_carries_the_measuring_marks(tmp_path: Path) -> None:
    path = tmp_path / "marks.pdf"

    write_sheet(cards(1), path)

    assert f"{REFERENCE_LENGTH_MM:g} mm" in page_text(path)


def test_the_measuring_marks_name_the_expected_barcode_width(tmp_path: Path) -> None:
    path = tmp_path / "width.pdf"

    write_sheet(cards(1), path)

    assert "37.3 mm wide" in page_text(path)


def test_the_measuring_marks_can_be_turned_off(tmp_path: Path) -> None:
    path = tmp_path / "bare.pdf"

    write_sheet(cards(1), path, calibration=False)

    assert f"{REFERENCE_LENGTH_MM:g} mm" not in page_text(path)


def test_the_measuring_marks_do_not_stop_the_barcodes_decoding(tmp_path: Path) -> None:
    path = tmp_path / "full.pdf"
    batch = cards(9)

    write_sheet(batch, path)

    assert sorted(decode_pdf(path)) == sorted(card.barcode for card in batch)


def test_every_barcode_still_decodes_from_a_black_and_white_print(tmp_path: Path) -> None:
    path = tmp_path / "grey.pdf"
    batch = cards(9)

    write_sheet(batch, path)

    pages = render_pdf_pages(path, dpi=300)
    grey = pages[0].convert("L").convert("RGB")
    assert sorted(decode_image(grey)) == sorted(card.barcode for card in batch)


def test_the_cut_marks_stay_clear_of_the_trimmed_card(tmp_path: Path) -> None:
    path = tmp_path / "marks-clear.pdf"
    layout = SheetLayout()

    write_sheet(cards(1), path, layout=layout)

    per_mm = 300 / 25.4
    image = render_pdf_pages(path, dpi=300)[0].convert("L")
    x, y = layout.positions()[0]
    column = int((x + layout.card_width_mm / 2) * per_mm)
    top = int((layout.page_height_mm - (y + layout.card_height_mm + layout.bleed_mm)) * per_mm)
    grey = image.tobytes()
    assert grey[(top - 2) * image.width + column] > 200


def test_a_print_shop_pdf_has_one_card_per_page(tmp_path: Path) -> None:
    path = tmp_path / "shop.pdf"
    batch = cards(3)

    pages = write_sheet(batch, path, layout=SheetLayout.print_shop())

    assert pages == 3
    assert sorted(decode_pdf(path)) == sorted(card.barcode for card in batch)


def test_a_print_shop_page_carries_no_ruler(tmp_path: Path) -> None:
    path = tmp_path / "shop-plain.pdf"

    write_sheet(cards(1), path, layout=SheetLayout.print_shop())

    assert "Ruler" not in page_text(path)
