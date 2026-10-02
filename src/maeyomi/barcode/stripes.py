"""The stripe track an Advanced Pico Beena card carries along one long edge.

A Beena card has twelve places for a bar along its bottom edge. A bar is a one
and an empty place a zero, read from the left end, and the console's reader
hands the game the twelve bits they spell with the leftmost lowest. The
positions were measured on the scans of real cards in MAME's software list, at
600 dots per inch: the bars are 2.88 mm wide, their centres 6.28 mm apart, the
first 10.07 mm from the left edge, each 15 mm tall and ending 0.4 mm short of
the edge. The real cards are landscape, and so is the printed card: the track
runs along its bottom edge with the first place at the left. A code is written
as the twelve places in that order, 1 for a bar. The card's face starts 2 mm
above the track, so neither its colour nor the bleed around it can darken a
place left empty.
"""

import re
from dataclasses import dataclass
from typing import Final

from PIL.Image import Image
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.said import Said


@dataclass(frozen=True, slots=True)
class Track:
    """Where a card's places sit: how many, how far apart, how wide and how long its bars are."""

    places: int
    pitch_mm: float
    bar_thickness_mm: float
    first_slot_mm: float
    bar_length_mm: float
    edge_gap_mm: float

    @property
    def depth_mm(self) -> float:
        """How far in from the edge the bars reach."""
        return self.edge_gap_mm + self.bar_length_mm


BEENA_TRACK: Final = Track(
    places=12,
    pitch_mm=6.28,
    bar_thickness_mm=2.88,
    first_slot_mm=10.07,
    bar_length_mm=15.0,
    edge_gap_mm=0.4,
)
TRACKS: Final = {track.places: track for track in (BEENA_TRACK,)}
TRACK_CLEARANCE_MM: Final = 2.0
BAR: Final = "1"
INK_LEVEL: Final = 128
MM_PER_INCH: Final = 25.4
STRIPES: Final = re.compile(r"[01]+")
WRONG_FORM: Final = Said(
    "a Beena card carries 12 places, each 1 for a bar or 0 for none",
    "ビーナの カードは 12この ばしょに バーが あれば 1、なければ 0",
)


def validate_stripes(code: str) -> str:
    """The code with spaces trimmed, or a refusal when it is not a track's ones and zeros."""
    body = code.strip()
    if not (STRIPES.fullmatch(body) and len(body) in TRACKS):
        raise UnsupportedBarcodeError(barcode=code, reason=WRONG_FORM)
    return body


def track_of(code: str) -> Track:
    """The track a code's length names."""
    return TRACKS[len(validate_stripes(code))]


def stripes_size_mm(code: str) -> tuple[float, float]:
    """How far the track runs and how tall its bars are, in millimetres."""
    track = track_of(code)
    return (track.places - 1) * track.pitch_mm + track.bar_thickness_mm, track.bar_length_mm


def bar_boxes(
    code: str, *, x_mm: float, y_mm: float
) -> tuple[tuple[float, float, float, float], ...]:
    """Each bar as left, bottom, width and height, for a card whose lower left corner is given."""
    track = track_of(code)
    return tuple(
        (
            x_mm + track.first_slot_mm + place * track.pitch_mm - track.bar_thickness_mm / 2,
            y_mm + track.edge_gap_mm,
            track.bar_thickness_mm,
            track.bar_length_mm,
        )
        for place, bit in enumerate(validate_stripes(code))
        if bit == BAR
    )


def draw_stripes(canvas: Canvas, code: str, *, x_mm: float, y_mm: float) -> None:
    """Draw the track along the bottom edge of a card whose lower left corner is given."""
    canvas.setFillColorRGB(0, 0, 0)
    for left, bottom, width, height in bar_boxes(code, x_mm=x_mm, y_mm=y_mm):
        canvas.rect(left * mm, bottom * mm, width * mm, height * mm, stroke=0, fill=1)


def read_stripes(image: Image, *, dpi: int, track: Track) -> str:
    """The code a card's track spells, sampled at each place on an image of the whole card."""
    gray = image.convert("L")
    row = gray.height - 1 - round((track.edge_gap_mm + track.bar_length_mm / 2) / MM_PER_INCH * dpi)
    columns = (
        round((track.first_slot_mm + place * track.pitch_mm) / MM_PER_INCH * dpi)
        for place in range(track.places)
    )
    levels = (gray.getpixel((column, row)) for column in columns)
    return "".join(BAR if isinstance(level, int) and level < INK_LEVEL else "0" for level in levels)
