"""Tests for reading a rendered barcode back off the page."""

from pathlib import Path

from PIL import Image
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.geometry import BarcodeGeometry
from barcode_battler.barcode.symbol import draw_symbol, symbol_size_mm
from barcode_battler.barcode.verify import decode_image, decode_pdf


def one_page(path: Path, codes: list[str]) -> None:
    geometry = BarcodeGeometry()
    width, height = symbol_size_mm(codes[0], geometry)
    canvas = Canvas(str(path), pagesize=((width + 20) * mm, (height + 20) * mm * len(codes)))
    for index, code in enumerate(codes):
        draw_symbol(canvas, code, x_mm=10, y_mm=10 + index * (height + 10), geometry=geometry)
    canvas.showPage()
    canvas.save()


def test_a_rendered_page_decodes_back_to_its_digits(tmp_path: Path) -> None:
    path = tmp_path / "one.pdf"

    one_page(path, ["0401207237501"])

    assert decode_pdf(path) == ["0401207237501"]


def test_every_symbol_on_a_page_is_found(tmp_path: Path) -> None:
    path = tmp_path / "many.pdf"
    codes = ["0401207237501", "0341011384506", "1954840299829"]

    one_page(path, codes)

    assert sorted(decode_pdf(path)) == sorted(codes)


def test_a_blank_image_yields_nothing() -> None:
    blank = Image.new("RGB", (400, 200), "white")

    assert decode_image(blank) == []


def test_a_lower_rasterisation_still_reads_a_nominal_symbol(tmp_path: Path) -> None:
    path = tmp_path / "low.pdf"

    one_page(path, ["0401207237501"])

    assert decode_pdf(path, dpi=300) == ["0401207237501"]
