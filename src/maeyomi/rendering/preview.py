"""Rasterise what the printer would produce, for showing on a screen.

The preview is the print renderer with a rasteriser on the end, never a second
drawing of the same card. A screen preview that is drawn separately from the
print output will eventually disagree with it, and the disagreement is exactly
the kind nobody notices until a sheet comes out of the printer wrong.
"""

import io
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from PIL.Image import Image
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.barcode.geometry import BarcodeGeometry
from maeyomi.barcode.rasterise import render_pdf_pages
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.rendering.card import CardStyle, draw_card
from maeyomi.rendering.layout import (
    POKER_CARD_HEIGHT_MM,
    POKER_CARD_WIDTH_MM,
    SheetLayout,
)
from maeyomi.rendering.sheet import write_sheet

CARD_PREVIEW_DPI: Final = 150
SHEET_PREVIEW_DPI: Final = 96


def card_png(
    card: GeneratedCard,
    *,
    dpi: int = CARD_PREVIEW_DPI,
    width_mm: float = POKER_CARD_WIDTH_MM,
    height_mm: float = POKER_CARD_HEIGHT_MM,
    geometry: BarcodeGeometry | None = None,
    style: CardStyle | None = None,
) -> bytes:
    """Render one card on its own and return it as PNG bytes."""
    with tempfile.TemporaryDirectory(prefix="maeyomi-preview-") as directory:
        path = Path(directory) / "card.pdf"
        canvas = Canvas(str(path), pagesize=(width_mm * mm, height_mm * mm))
        draw_card(
            canvas,
            card,
            x_mm=0,
            y_mm=0,
            width_mm=width_mm,
            height_mm=height_mm,
            geometry=geometry or BarcodeGeometry(),
            style=style,
        )
        canvas.showPage()
        canvas.save()
        return _encode(render_pdf_pages(path, dpi=dpi)[0])


def sheet_png_pages(
    cards: Sequence[GeneratedCard],
    *,
    dpi: int = SHEET_PREVIEW_DPI,
    layout: SheetLayout | None = None,
    geometry: BarcodeGeometry | None = None,
    style: CardStyle | None = None,
) -> list[bytes]:
    """Render a full sheet and return one PNG per page."""
    if not cards:
        return []
    with tempfile.TemporaryDirectory(prefix="maeyomi-preview-") as directory:
        path = Path(directory) / "sheet.pdf"
        write_sheet(cards, path, layout=layout, geometry=geometry, style=style)
        return [_encode(page) for page in render_pdf_pages(path, dpi=dpi)]


def _encode(image: Image) -> bytes:
    """Encode a rendered page as PNG bytes."""
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, "PNG")
    return buffer.getvalue()
