"""Marks that let someone check whether their printer scaled the page.

A print dialog set to "fit to page", "shrink to fit", or any magnification
other than 100 percent changes the module width, and a barcode printed at the
wrong module width stops reading while still looking perfectly normal. Nothing
else on the page reveals that.

So the foot of every sheet carries a ruler of a known length, numbered in
centimetres, and a line naming the width each barcode should measure. A ruler
held against either one answers the question in a second, and
`scale_error_percent` turns the measurement into the correction to type into
the print dialog.

Both the ruler and the note sit in one band below the card grid, clear of the
cut marks and at least 5 mm from the paper's edge, which most printers can
reach. Three rows of cards leave 18.3 mm for marks on A4, and a ruler whose
numbers start 5 mm in needs more than half of that, so splitting the marks
between the head and the foot costs a row. One band keeps the row and puts both
marks on the same offcut. The note is printed in English and in Japanese, like
the cards.
"""

from typing import Final

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.rendering.text import font_for

RULER_LENGTH_MM: Final = 100
REFERENCE_LENGTH_MM: Final = float(RULER_LENGTH_MM)
"""The length a ruler is held against. The printed ruler is exactly this long."""

RULER_MAJOR_MM: Final = 10
RULER_MINOR_MM: Final = 5
MAJOR_TICK_MM: Final = 3.0
MINOR_TICK_MM: Final = 1.8
LINE_WIDTH: Final = 0.4
LABEL_FONT: Final = "Helvetica"
LABEL_SIZE_PT: Final = 6.0

NUMBER_BASELINE_MM: Final = 5.2
RULER_BASELINE_MM: Final = 10.0
ENGLISH_NOTE_BASELINE_MM: Final = 11.0
JAPANESE_NOTE_BASELINE_MM: Final = 13.5
FULL_WIDTH_CAP_MM: Final = 2.0
"""How far a full-width Japanese glyph rises above its baseline at this size.

Latin type at 6 pt rises about 1.5 mm, and a band sized for that leaves the
Japanese line standing 0.4 mm proud of it, which is where the cut marks come
down.
"""
FOOT_BAND_MM: Final = JAPANESE_NOTE_BASELINE_MM + FULL_WIDTH_CAP_MM
"""What the grid must keep clear at the foot, measured from what is drawn there.

The Japanese note is the highest thing in the band, so this follows its
baseline rather than being chosen separately. A band chosen independently
drifts below what the marks need, and then they are drawn across the bottom row
of cards.
"""


def draw_calibration(
    canvas: Canvas,
    *,
    page_width_mm: float,
    page_height_mm: float,
    symbol_width_mm: float,
) -> None:
    """Draw the ruler, its numbers and the note explaining what to do with them."""
    if page_width_mm < RULER_LENGTH_MM or page_height_mm < FOOT_BAND_MM:
        message = (
            f"a page of {page_width_mm} by {page_height_mm} mm cannot hold the "
            f"{RULER_LENGTH_MM} mm ruler and its {FOOT_BAND_MM} mm band"
        )
        raise ValueError(message)
    origin = (page_width_mm - RULER_LENGTH_MM) / 2
    _draw_ruler(canvas, origin)
    _draw_note(canvas, centre=page_width_mm / 2, symbol_width_mm=symbol_width_mm)


def scale_error_percent(measured_mm: float, *, reference_mm: float = REFERENCE_LENGTH_MM) -> float:
    """How far a print is from full size, as a percentage.

    Zero means the print is correct. A negative value means it came out small,
    so the print dialog needs that much added back.
    """
    if measured_mm <= 0:
        message = f"measured length must be above zero, got {measured_mm}"
        raise ValueError(message)
    return (measured_mm - reference_mm) / reference_mm * 100


def _draw_ruler(canvas: Canvas, origin: float) -> None:
    """Draw a centimetre ruler with its major ticks numbered beneath."""
    canvas.setLineWidth(LINE_WIDTH)
    canvas.line(
        origin * mm,
        RULER_BASELINE_MM * mm,
        (origin + RULER_LENGTH_MM) * mm,
        RULER_BASELINE_MM * mm,
    )
    canvas.setFont(LABEL_FONT, LABEL_SIZE_PT)
    for offset in range(0, RULER_LENGTH_MM + 1, RULER_MINOR_MM):
        major = offset % RULER_MAJOR_MM == 0
        height = MAJOR_TICK_MM if major else MINOR_TICK_MM
        x = origin + offset
        canvas.line(x * mm, RULER_BASELINE_MM * mm, x * mm, (RULER_BASELINE_MM - height) * mm)
        if major:
            canvas.drawCentredString(x * mm, NUMBER_BASELINE_MM * mm, str(offset // RULER_MAJOR_MM))


def _draw_note(canvas: Canvas, *, centre: float, symbol_width_mm: float) -> None:
    """Say what the ruler is for, in English and then in Japanese."""
    english = (
        f"The ruler at the foot of this page is {RULER_LENGTH_MM:g} mm, numbered in cm. "
        f"Each barcode should be {symbol_width_mm:.1f} mm wide. "
        "Shorter means the printer scaled the page: reprint at 100 percent."
    )
    japanese = (
        f"したの ものさしは {RULER_LENGTH_MM:g} mm です。"
        f"バーコードの はばは {symbol_width_mm:.1f} mm。"
        "みじかい ときは 100% で いんさつ しなおしてね。"
    )
    canvas.setFont(LABEL_FONT, LABEL_SIZE_PT)
    canvas.drawCentredString(centre * mm, ENGLISH_NOTE_BASELINE_MM * mm, english)
    canvas.setFont(font_for(japanese), LABEL_SIZE_PT)
    canvas.drawCentredString(centre * mm, JAPANESE_NOTE_BASELINE_MM * mm, japanese)
