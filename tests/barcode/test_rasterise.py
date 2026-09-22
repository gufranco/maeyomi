"""Tests for turning a PDF page back into pixels."""

from pathlib import Path

import pytest
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.barcode.rasterise import ink_box, render_pdf_pages


def blank_pdf(path: Path, pages: int) -> None:
    canvas = Canvas(str(path), pagesize=(50 * mm, 30 * mm))
    for _ in range(pages):
        canvas.showPage()
    canvas.save()


def marked_pdf(path: Path) -> None:
    canvas = Canvas(str(path), pagesize=(50 * mm, 30 * mm))
    canvas.rect(10 * mm, 10 * mm, 20 * mm, 5 * mm, fill=1)
    canvas.showPage()
    canvas.save()


def test_every_page_is_rendered(tmp_path: Path) -> None:
    path = tmp_path / "three.pdf"
    blank_pdf(path, 3)

    assert len(render_pdf_pages(path, dpi=72)) == 3


def test_the_rendered_size_follows_the_requested_resolution(tmp_path: Path) -> None:
    path = tmp_path / "one.pdf"
    blank_pdf(path, 1)

    low = render_pdf_pages(path, dpi=72)[0]
    high = render_pdf_pages(path, dpi=144)[0]

    assert high.width == low.width * 2


def test_a_blank_page_has_no_ink(tmp_path: Path) -> None:
    path = tmp_path / "blank.pdf"
    blank_pdf(path, 1)

    assert ink_box(render_pdf_pages(path, dpi=150)[0]) is None


def test_a_marked_page_reports_the_extent_of_its_ink(tmp_path: Path) -> None:
    path = tmp_path / "marked.pdf"
    marked_pdf(path)

    box = ink_box(render_pdf_pages(path, dpi=254)[0])

    assert box is not None
    width_mm = (box[2] - box[0]) / (254 / 25.4)
    assert width_mm == pytest.approx(20.0, abs=0.6)
