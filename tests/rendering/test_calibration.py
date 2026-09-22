"""Tests for the printed measuring marks."""

from pathlib import Path

import pypdfium2 as pdfium
import pytest
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.barcode.rasterise import ink_box, render_pdf_pages
from maeyomi.rendering.calibration import (
    FOOT_BAND_MM,
    JAPANESE_NOTE_BASELINE_MM,
    REFERENCE_LENGTH_MM,
    RULER_BASELINE_MM,
    RULER_LENGTH_MM,
    draw_calibration,
    scale_error_percent,
)
from maeyomi.rendering.layout import SheetLayout

MEASURE_DPI = 600


def page(path: Path, width_mm: float = 210.0, height_mm: float = 297.0) -> None:
    canvas = Canvas(str(path), pagesize=(width_mm * mm, height_mm * mm))
    draw_calibration(
        canvas, page_width_mm=width_mm, page_height_mm=height_mm, symbol_width_mm=37.29
    )
    canvas.showPage()
    canvas.save()


def text_of(path: Path) -> str:
    document = pdfium.PdfDocument(str(path))
    try:
        return str(document[0].get_textpage().get_text_range())
    finally:
        document.close()


def test_the_reference_length_is_printed_with_its_value(tmp_path: Path) -> None:
    path = tmp_path / "marks.pdf"

    page(path)

    assert f"{REFERENCE_LENGTH_MM:g} mm" in text_of(path)


def test_the_expected_symbol_width_is_printed(tmp_path: Path) -> None:
    path = tmp_path / "marks.pdf"

    page(path)

    assert "37.3" in text_of(path)


def test_the_reference_line_measures_what_it_claims(tmp_path: Path) -> None:
    path = tmp_path / "line.pdf"
    canvas = Canvas(str(path), pagesize=(REFERENCE_LENGTH_MM * mm, 20 * mm))
    canvas.setLineWidth(0.4)
    canvas.line(0, 10 * mm, REFERENCE_LENGTH_MM * mm, 10 * mm)
    canvas.showPage()
    canvas.save()

    box = ink_box(render_pdf_pages(path, dpi=MEASURE_DPI)[0])

    assert box is not None
    assert (box[2] - box[0]) / (MEASURE_DPI / 25.4) == pytest.approx(REFERENCE_LENGTH_MM, abs=0.2)


def test_the_marks_stay_inside_the_page(tmp_path: Path) -> None:
    path = tmp_path / "inside.pdf"

    page(path)

    image = render_pdf_pages(path, dpi=150)[0]
    box = ink_box(image)
    assert box is not None
    assert box[0] >= 0
    assert box[2] <= image.width


def test_the_ruler_is_the_stated_length() -> None:
    assert RULER_LENGTH_MM > 0
    assert RULER_LENGTH_MM % 10 == 0


@pytest.mark.parametrize(
    ("measured", "expected"),
    [(100.0, 0.0), (96.0, -4.0), (104.0, 4.0)],
)
def test_the_scale_error_is_reported_as_a_percentage(measured: float, expected: float) -> None:
    assert scale_error_percent(measured, reference_mm=100.0) == pytest.approx(expected)


def test_a_non_positive_measurement_is_rejected() -> None:
    with pytest.raises(ValueError, match="above zero"):
        scale_error_percent(0.0, reference_mm=100.0)


def test_a_page_too_small_for_the_marks_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot hold"):
        page(tmp_path / "tiny.pdf", width_mm=80.0, height_mm=120.0)


def test_a_page_too_short_for_the_band_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot hold"):
        page(tmp_path / "flat.pdf", width_mm=210.0, height_mm=10.0)


def test_the_note_is_printed_in_both_languages(tmp_path: Path) -> None:
    path = tmp_path / "bilingual.pdf"

    page(path)

    text = text_of(path)
    assert "reprint at 100 percent" in text
    assert "100%" in text
    assert "いんさつ" in text


def test_the_note_sits_well_inside_the_printable_area(tmp_path: Path) -> None:
    path = tmp_path / "margins.pdf"

    page(path)

    image = render_pdf_pages(path, dpi=150)[0]
    box = ink_box(image)
    assert box is not None
    per_mm = 150 / 25.4
    assert box[1] >= 5.0 * per_mm
    assert image.height - box[3] >= 5.0 * per_mm


def test_every_mark_stays_inside_the_band_the_grid_keeps_clear() -> None:
    assert RULER_BASELINE_MM < FOOT_BAND_MM
    assert JAPANESE_NOTE_BASELINE_MM < FOOT_BAND_MM


def test_no_card_reaches_the_marks() -> None:
    layout = SheetLayout()

    lowest = min(y for _, y in layout.positions())

    assert lowest >= FOOT_BAND_MM


def test_keeping_the_band_honest_still_leaves_three_rows() -> None:
    assert SheetLayout().cards_per_page == 9


def test_a_sheet_without_marks_uses_the_whole_page() -> None:
    bare = SheetLayout(marks=False)

    assert min(y for _, y in bare.positions()) < FOOT_BAND_MM
