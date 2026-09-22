"""Tests for drawing an EAN symbol as vectors and reading it back."""

from pathlib import Path

import pytest
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.geometry import BarcodeGeometry
from barcode_battler.barcode.rasterise import ink_box, render_pdf_pages
from barcode_battler.barcode.symbol import draw_symbol, symbol_size_mm
from barcode_battler.barcode.verify import decode_pdf

MARGIN_MM = 10.0
MEASURE_DPI = 600


def write_pdf(path: Path, code: str, geometry: BarcodeGeometry) -> tuple[float, float]:
    width, height = symbol_size_mm(code, geometry)
    canvas = Canvas(
        str(path), pagesize=((width + 2 * MARGIN_MM) * mm, (height + 2 * MARGIN_MM) * mm)
    )
    draw_symbol(canvas, code, x_mm=MARGIN_MM, y_mm=MARGIN_MM, geometry=geometry)
    canvas.showPage()
    canvas.save()
    return width, height


def ink_size_mm(path: Path) -> tuple[float, float]:
    box = ink_box(render_pdf_pages(path, dpi=MEASURE_DPI)[0])
    assert box is not None
    per_mm = MEASURE_DPI / 25.4
    return (box[2] - box[0]) / per_mm, (box[3] - box[1]) / per_mm


def test_a_thirteen_digit_symbol_decodes_back_to_its_digits(tmp_path: Path) -> None:
    path = tmp_path / "ean13.pdf"

    write_pdf(path, "0401207237501", BarcodeGeometry())

    assert decode_pdf(path) == ["0401207237501"]


def test_an_eight_digit_symbol_decodes_back_to_its_digits(tmp_path: Path) -> None:
    path = tmp_path / "ean8.pdf"

    write_pdf(path, "49123456", BarcodeGeometry())

    assert decode_pdf(path) == ["49123456"]


@pytest.mark.parametrize("module_width", [0.264, 0.33, 0.45, 0.66])
def test_a_symbol_decodes_at_every_permitted_module_width(
    tmp_path: Path, module_width: float
) -> None:
    path = tmp_path / f"width-{module_width}.pdf"

    write_pdf(path, "0401207237501", BarcodeGeometry(module_width_mm=module_width))

    assert decode_pdf(path) == ["0401207237501"]


@pytest.mark.parametrize(("code", "length"), [("0401207237501", 13), ("49123456", 8)])
def test_the_drawn_width_is_at_least_the_standard_minimum(code: str, length: int) -> None:
    geometry = BarcodeGeometry(module_width_mm=0.33)

    width, _ = symbol_size_mm(code, geometry)

    assert width == pytest.approx(
        geometry.total_width_mm(length)
    ) or width > geometry.total_width_mm(length)


def test_a_thirteen_digit_symbol_is_the_exact_standard_width() -> None:
    geometry = BarcodeGeometry(module_width_mm=0.33)

    width, _ = symbol_size_mm("0401207237501", geometry)

    assert width / geometry.module_width_mm == pytest.approx(113.0)


def test_the_drawn_height_is_the_requested_height() -> None:
    geometry = BarcodeGeometry(module_width_mm=0.33, height_mm=18.0)

    _, height = symbol_size_mm("0401207237501", geometry)

    assert height == pytest.approx(18.0)


def test_the_bars_fit_inside_the_declared_width_leaving_the_quiet_zones_blank(
    tmp_path: Path,
) -> None:
    path = tmp_path / "quiet.pdf"
    geometry = BarcodeGeometry(show_digits=False)

    declared_width, _ = write_pdf(path, "0401207237501", geometry)
    ink_width, _ = ink_size_mm(path)

    assert ink_width < declared_width
    assert declared_width - ink_width >= geometry.right_quiet_zone_mm(13)


def test_the_human_readable_digits_are_printed_beside_the_bars(tmp_path: Path) -> None:
    with_digits = tmp_path / "with.pdf"
    without_digits = tmp_path / "without.pdf"

    write_pdf(with_digits, "0401207237501", BarcodeGeometry(show_digits=True))
    write_pdf(without_digits, "0401207237501", BarcodeGeometry(show_digits=False))

    assert ink_size_mm(with_digits)[0] > ink_size_mm(without_digits)[0]


def test_a_code_that_is_not_a_valid_barcode_is_rejected() -> None:
    with pytest.raises(ValueError, match="check digit"):
        symbol_size_mm("0401207237509", BarcodeGeometry())


def test_a_twelve_digit_code_is_rejected() -> None:
    with pytest.raises(ValueError, match="8 or 13"):
        symbol_size_mm("040120723750", BarcodeGeometry())
