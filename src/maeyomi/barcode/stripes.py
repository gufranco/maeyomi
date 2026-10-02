"""The stripe track an Advanced Pico Beena card carries along one long edge.

A Beena card has twelve places for a bar along its bottom edge. A bar is a one
and an empty place a zero, read from the left end, and the console's reader
hands the game the twelve bits they spell with the leftmost lowest. The
positions were measured on the scans of real cards in MAME's software list, at
600 dots per inch: the bars are 2.88 mm wide, their centres 6.28 mm apart, the
first 10.07 mm from the left edge, each 15 mm tall and ending 0.4 mm short of
the edge. Printed on a portrait card, the card's bottom edge becomes its left
edge, so the track runs down the left side with the first place at the top.
A code is written as the twelve places in that order, 1 for a bar. The card's
face starts 2 mm clear of the track, so neither its colour nor the bleed
around it can darken a place left empty.
"""

import re
from typing import Final

from PIL.Image import Image
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.said import Said

SLOTS: Final = 12
PITCH_MM: Final = 6.28
BAR_THICKNESS_MM: Final = 2.88
FIRST_SLOT_MM: Final = 10.07
BAR_LENGTH_MM: Final = 15.0
EDGE_GAP_MM: Final = 0.4
TRACK_DEPTH_MM: Final = EDGE_GAP_MM + BAR_LENGTH_MM
TRACK_CLEARANCE_MM: Final = 2.0
BAR: Final = "1"
INK_LEVEL: Final = 128
MM_PER_INCH: Final = 25.4
STRIPES: Final = re.compile(r"[01]{12}")
WRONG_FORM: Final = Said(
    "a Beena card carries 12 places, each 1 for a bar or 0 for none",
    "ビーナの カードは 12この ばしょに バーが あれば 1、なければ 0",
)


def validate_stripes(code: str) -> str:
    """The code with spaces trimmed, or a refusal when it is not twelve ones and zeros."""
    body = code.strip()
    if not STRIPES.fullmatch(body):
        raise UnsupportedBarcodeError(barcode=code, reason=WRONG_FORM)
    return body


def stripes_size_mm(code: str) -> tuple[float, float]:
    """How long the bars are and how far the track runs, in millimetres."""
    validate_stripes(code)
    return BAR_LENGTH_MM, (SLOTS - 1) * PITCH_MM + BAR_THICKNESS_MM


def bar_boxes(
    code: str, *, x_mm: float, y_mm: float, height_mm: float
) -> tuple[tuple[float, float, float, float], ...]:
    """Each bar as left, bottom, width and height, for a card whose lower left corner is given."""
    top = y_mm + height_mm
    return tuple(
        (
            x_mm + EDGE_GAP_MM,
            top - FIRST_SLOT_MM - place * PITCH_MM - BAR_THICKNESS_MM / 2,
            BAR_LENGTH_MM,
            BAR_THICKNESS_MM,
        )
        for place, bit in enumerate(validate_stripes(code))
        if bit == BAR
    )


def draw_stripes(canvas: Canvas, code: str, *, x_mm: float, y_mm: float, height_mm: float) -> None:
    """Draw the track down the left edge of a card whose lower left corner is given."""
    canvas.setFillColorRGB(0, 0, 0)
    for left, bottom, width, height in bar_boxes(code, x_mm=x_mm, y_mm=y_mm, height_mm=height_mm):
        canvas.rect(left * mm, bottom * mm, width * mm, height * mm, stroke=0, fill=1)


def read_stripes(image: Image, *, dpi: int) -> str:
    """The code a card's track spells, sampled at each place on an image of the whole card."""
    gray = image.convert("L")
    column = round((EDGE_GAP_MM + BAR_LENGTH_MM / 2) / MM_PER_INCH * dpi)
    rows = (round((FIRST_SLOT_MM + place * PITCH_MM) / MM_PER_INCH * dpi) for place in range(SLOTS))
    levels = (gray.getpixel((column, row)) for row in rows)
    return "".join(BAR if isinstance(level, int) and level < INK_LEVEL else "0" for level in levels)
