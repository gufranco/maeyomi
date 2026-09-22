"""Write a printable sheet of cards as a PDF.

The PDF is the master output. Raster formats are produced by rasterising it, so
there is one renderer, one geometry and one thing to verify.
"""

import itertools
from collections.abc import Sequence
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.geometry import BarcodeGeometry
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.rendering.calibration import draw_calibration
from barcode_battler.rendering.card import CardStyle, draw_card
from barcode_battler.rendering.layout import SheetLayout

CUT_MARK_LENGTH_MM = 4.0
CUT_MARK_LINE_WIDTH = 0.25


def write_sheet(
    cards: Sequence[GeneratedCard],
    path: str | Path,
    *,
    layout: SheetLayout | None = None,
    geometry: BarcodeGeometry | None = None,
    style: CardStyle | None = None,
    cut_marks: bool = True,
    calibration: bool = True,
) -> int:
    """Write every card across as many pages as it takes, and return the page count."""
    if not cards:
        return 0
    resolved_layout = layout or SheetLayout()
    resolved_geometry = geometry or BarcodeGeometry()
    canvas = Canvas(
        str(path),
        pagesize=(resolved_layout.page_width_mm * mm, resolved_layout.page_height_mm * mm),
    )
    pages = 0
    for page in _pages(cards, resolved_layout.cards_per_page):
        _draw_page(
            canvas,
            page,
            resolved_layout,
            resolved_geometry,
            style,
            cut_marks=cut_marks,
            calibration=calibration,
        )
        canvas.showPage()
        pages += 1
    canvas.save()
    return pages


def _pages(cards: Sequence[GeneratedCard], per_page: int) -> list[Sequence[GeneratedCard]]:
    """Split the cards into one list per sheet."""
    return [cards[start : start + per_page] for start in range(0, len(cards), per_page)]


def _draw_page(
    canvas: Canvas,
    cards: Sequence[GeneratedCard],
    layout: SheetLayout,
    geometry: BarcodeGeometry,
    style: CardStyle | None,
    *,
    cut_marks: bool,
    calibration: bool,
) -> None:
    """Draw one sheet of cards, the marks to cut them apart and the ruler to check the scale."""
    for card, (x_mm, y_mm) in zip(cards, layout.positions(), strict=False):
        draw_card(
            canvas,
            card,
            x_mm=x_mm,
            y_mm=y_mm,
            width_mm=layout.card_width_mm,
            height_mm=layout.card_height_mm,
            geometry=geometry,
            style=style,
        )
    if cut_marks:
        _draw_cut_marks(canvas, layout)
    if calibration:
        draw_calibration(
            canvas,
            page_width_mm=layout.page_width_mm,
            page_height_mm=layout.page_height_mm,
            symbol_width_mm=geometry.total_width_mm(13),
        )


def _draw_cut_marks(canvas: Canvas, layout: SheetLayout) -> None:
    """Draw short marks in the page margins aligned with every card edge."""
    canvas.setLineWidth(CUT_MARK_LINE_WIDTH)
    for x_mm in _edges(layout, horizontal=True):
        _mark(canvas, x_mm, 0, x_mm, CUT_MARK_LENGTH_MM)
        _mark(
            canvas,
            x_mm,
            layout.page_height_mm - CUT_MARK_LENGTH_MM,
            x_mm,
            layout.page_height_mm,
        )
    for y_mm in _edges(layout, horizontal=False):
        _mark(canvas, 0, y_mm, CUT_MARK_LENGTH_MM, y_mm)
        _mark(
            canvas,
            layout.page_width_mm - CUT_MARK_LENGTH_MM,
            y_mm,
            layout.page_width_mm,
            y_mm,
        )


def _edges(layout: SheetLayout, *, horizontal: bool) -> list[float]:
    """Every card edge along one axis, in millimetres."""
    positions = layout.positions()
    size = layout.card_width_mm if horizontal else layout.card_height_mm
    index = 0 if horizontal else 1
    starts = {round(position[index], 4) for position in positions}
    return sorted(itertools.chain(starts, (start + size for start in starts)))


def _mark(canvas: Canvas, x1_mm: float, y1_mm: float, x2_mm: float, y2_mm: float) -> None:
    """Draw one cut mark, taking millimetres."""
    canvas.line(x1_mm * mm, y1_mm * mm, x2_mm * mm, y2_mm * mm)
