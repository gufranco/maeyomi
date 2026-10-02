"""Tests for the stripe track a Sega Toys card carries along one long edge."""

from itertools import pairwise
from pathlib import Path

import pytest
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.barcode.rasterise import render_pdf_pages
from maeyomi.barcode.stripes import (
    BEENA_TRACK,
    OCHAKEN_TRACK,
    Track,
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
OCHAKEN_CODE = "0101000000001001"
CARD_WIDTH = 88.9
CARD_HEIGHT = 63.5
DPI = 300


def page(path: Path, code: str) -> None:
    canvas = Canvas(str(path), pagesize=(CARD_WIDTH * mm, CARD_HEIGHT * mm))
    draw_stripes(canvas, code, x_mm=0, y_mm=0)
    canvas.save()


def test_a_bar_is_drawn_for_every_one_and_none_for_a_zero() -> None:
    boxes = bar_boxes(CODE, x_mm=0, y_mm=0)

    assert len(boxes) == CODE.count("1")


@pytest.mark.parametrize(("code", "track"), [(CODE, BEENA_TRACK), (OCHAKEN_CODE, OCHAKEN_TRACK)])
def test_the_first_bar_sits_along_the_bottom_edge_where_the_cards_does(
    code: str, track: Track
) -> None:
    first = code.index("1")

    x, y, width, height = bar_boxes(code, x_mm=0, y_mm=0)[0]

    assert x + width / 2 == pytest.approx(track.first_slot_mm + first * track.pitch_mm)
    assert (width, y, y + height) == pytest.approx(
        (track.bar_thickness_mm, track.edge_gap_mm, track.depth_mm)
    )


@pytest.mark.parametrize("track", [BEENA_TRACK, OCHAKEN_TRACK])
def test_bars_are_one_pitch_apart_left_to_right(track: Track) -> None:
    boxes = bar_boxes("1" * track.places, x_mm=0, y_mm=0)

    gaps = {round(right[0] - left[0], 6) for left, right in pairwise(boxes)}
    assert gaps == {round(track.pitch_mm, 6)}


@pytest.mark.parametrize(("code", "track"), [(CODE, BEENA_TRACK), (OCHAKEN_CODE, OCHAKEN_TRACK)])
def test_a_drawn_track_reads_back_as_its_code(tmp_path: Path, code: str, track: Track) -> None:
    path = tmp_path / "track.pdf"
    page(path, code)

    image = render_pdf_pages(path, dpi=DPI)[0]

    assert read_stripes(image, dpi=DPI, track=track) == code


def test_a_codes_length_names_its_track() -> None:
    assert (track_of(CODE), track_of(OCHAKEN_CODE)) == (BEENA_TRACK, OCHAKEN_TRACK)


@pytest.mark.parametrize(
    "code", ["1000101100", "10001011001A", "1000101100110", "", "10001011001100110"]
)
def test_a_code_no_track_carries_is_refused_in_both_languages(code: str) -> None:
    with pytest.raises(UnsupportedBarcodeError, match="12 places, or 16") as raised:
        validate_stripes(code)

    assert in_japanese(raised.value.args[0])


@pytest.mark.parametrize("code", [CODE, OCHAKEN_CODE])
def test_a_valid_code_is_returned_unchanged(code: str) -> None:
    assert validate_stripes(f" {code} ") == code


def test_the_track_is_as_long_as_its_bars_and_spans_every_place() -> None:
    assert stripes_size_mm(CODE) == pytest.approx((11 * 6.28 + 2.88, 15.0))
    assert stripes_size_mm(OCHAKEN_CODE) == pytest.approx((15 * 4.0 + 3.93, 8.17))
