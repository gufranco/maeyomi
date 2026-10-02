"""Tests for the stripe track an Advanced Pico Beena card carries along one long edge."""

from itertools import pairwise
from pathlib import Path

import pytest
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.barcode.rasterise import render_pdf_pages
from maeyomi.barcode.stripes import (
    BEENA_TRACK,
    bar_boxes,
    draw_stripes,
    read_stripes,
    stripes_size_mm,
    track_of,
    validate_stripes,
)
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.said import in_japanese

CODE = "100010110011"
CARD_WIDTH = 63.5
CARD_HEIGHT = 88.9
DPI = 300


def page(path: Path, code: str) -> None:
    canvas = Canvas(str(path), pagesize=(CARD_WIDTH * mm, CARD_HEIGHT * mm))
    draw_stripes(canvas, code, x_mm=0, y_mm=0, height_mm=CARD_HEIGHT)
    canvas.save()


def test_a_bar_is_drawn_for_every_one_and_none_for_a_zero() -> None:
    boxes = bar_boxes(CODE, x_mm=0, y_mm=0, height_mm=CARD_HEIGHT)

    assert len(boxes) == CODE.count("1")


def test_the_first_bar_sits_where_the_cards_first_bar_does() -> None:
    x, y, width, height = bar_boxes(CODE, x_mm=0, y_mm=0, height_mm=CARD_HEIGHT)[0]

    assert y + height / 2 == pytest.approx(CARD_HEIGHT - BEENA_TRACK.first_slot_mm)
    assert height == BEENA_TRACK.bar_thickness_mm
    assert x + width == pytest.approx(BEENA_TRACK.depth_mm)


def test_bars_are_one_pitch_apart() -> None:
    boxes = bar_boxes("1" * BEENA_TRACK.places, x_mm=0, y_mm=0, height_mm=CARD_HEIGHT)

    gaps = {round(upper[1] - lower[1], 6) for upper, lower in pairwise(boxes)}
    assert gaps == {round(BEENA_TRACK.pitch_mm, 6)}


def test_a_drawn_track_reads_back_as_its_code(tmp_path: Path) -> None:
    path = tmp_path / "track.pdf"
    page(path, CODE)

    image = render_pdf_pages(path, dpi=DPI)[0]

    assert read_stripes(image, dpi=DPI, track=BEENA_TRACK) == CODE


def test_a_codes_length_names_its_track() -> None:
    assert track_of(CODE) == BEENA_TRACK


@pytest.mark.parametrize("code", ["1000101100", "10001011001A", "1000101100110", ""])
def test_a_code_that_is_not_twelve_ones_and_zeros_is_refused_in_both_languages(code: str) -> None:
    with pytest.raises(UnsupportedBarcodeError, match="12") as raised:
        validate_stripes(code)

    assert in_japanese(raised.value.args[0])


def test_a_valid_code_is_returned_unchanged() -> None:
    assert validate_stripes(f" {CODE} ") == CODE


def test_the_track_is_as_long_as_its_bars_and_spans_every_place() -> None:
    assert stripes_size_mm(CODE) == pytest.approx((15.0, 11 * 6.28 + 2.88))
