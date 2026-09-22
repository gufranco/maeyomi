"""Write a printable sheet of cards as a PDF.

The PDF is the master output. Raster formats are produced by rasterising it, so
there is one renderer, one geometry and one thing to verify.
"""

from collections.abc import Sequence
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.barcode.geometry import BarcodeGeometry
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.rendering.calibration import draw_calibration
from maeyomi.rendering.card import CardStyle, draw_card
from maeyomi.rendering.document import describe
from maeyomi.rendering.layout import CUT_MARK_LENGTH_MM, SheetLayout

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
    title: str | None = None,
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
    describe(canvas, title or _title(cards))
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
            bleed_mm=layout.bleed_mm,
        )
    if cut_marks and layout.marks:
        _draw_cut_marks(canvas, layout)
    if calibration and layout.marks:
        draw_calibration(
            canvas,
            page_width_mm=layout.page_width_mm,
            page_height_mm=layout.page_height_mm,
            symbol_width_mm=geometry.total_width_mm(13),
        )


def _draw_cut_marks(canvas: Canvas, layout: SheetLayout) -> None:
    """Draw two short marks at each corner of every card, outside its bleed.

    A printer cuts on the line the marks point at. They start at the edge of the
    bleed rather than at the trim line, so no mark is left on the card itself,
    and they are corner ticks rather than lines across the page, which is what
    print shops ask for.
    """
    canvas.setLineWidth(CUT_MARK_LINE_WIDTH)
    bleed = layout.bleed_mm
    for x_mm, y_mm in layout.positions():
        edges = (
            (x_mm, y_mm, -1, -1),
            (x_mm + layout.card_width_mm, y_mm, 1, -1),
            (x_mm, y_mm + layout.card_height_mm, -1, 1),
            (x_mm + layout.card_width_mm, y_mm + layout.card_height_mm, 1, 1),
        )
        for corner_x, corner_y, away_x, away_y in edges:
            start_x = corner_x + away_x * bleed
            start_y = corner_y + away_y * bleed
            _mark(canvas, start_x, corner_y, start_x + away_x * CUT_MARK_LENGTH_MM, corner_y)
            _mark(canvas, corner_x, start_y, corner_x, start_y + away_y * CUT_MARK_LENGTH_MM)


def _mark(canvas: Canvas, x1_mm: float, y1_mm: float, x2_mm: float, y2_mm: float) -> None:
    """Draw one cut mark, taking millimetres."""
    canvas.line(x1_mm * mm, y1_mm * mm, x2_mm * mm, y2_mm * mm)


def _title(cards: Sequence[GeneratedCard]) -> str:
    """Name the sheet after what is on it, for the reader who hears it spoken."""
    if len(cards) == 1:
        return f"Barcode Battler II card: {cards[0].name}"
    return f"Barcode Battler II cards: {len(cards)} to cut out"
