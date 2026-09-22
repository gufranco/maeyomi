"""Draw an EAN symbol as vectors at an exact module width.

ReportLab's EAN widgets are used rather than a rasterised image, because a
raster scaled to fit a layout rounds its module widths unevenly, which is a
scan failure that no test on the digit string would catch. The module width is
set explicitly and the symbol's size follows from it.

Quiet zones come from the widget's own `quiet` flag rather than from explicit
values, because its `lquiet` and `rquiet` attributes are declared as booleans
and reject a length. The width it produces is measured against the standard in
`test_symbol.py` rather than assumed.
"""

from typing import Final

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.eanbc import Ean8BarcodeWidget, Ean13BarcodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.geometry import EAN_8_LENGTH, EAN_13_LENGTH, BarcodeGeometry
from barcode_battler.decoder.validation import validate_barcode

_WIDGETS: Final = {EAN_13_LENGTH: Ean13BarcodeWidget, EAN_8_LENGTH: Ean8BarcodeWidget}


def symbol_size_mm(code: str, geometry: BarcodeGeometry) -> tuple[float, float]:
    """Return the width and height in millimetres the drawn symbol occupies."""
    drawing = _drawing(code, geometry)
    return drawing.width / mm, drawing.height / mm


def draw_symbol(
    canvas: Canvas, code: str, *, x_mm: float, y_mm: float, geometry: BarcodeGeometry
) -> tuple[float, float]:
    """Draw the symbol with its lower left corner at the given point, in millimetres."""
    drawing = _drawing(code, geometry)
    renderPDF.draw(drawing, canvas, x_mm * mm, y_mm * mm)
    return drawing.width / mm, drawing.height / mm


def _drawing(code: str, geometry: BarcodeGeometry) -> Drawing:
    """Build the symbol, rejecting a code the device itself would reject."""
    normalised = validate_barcode(code)
    widget_class = _WIDGETS[len(normalised)]
    widget = widget_class(
        normalised,
        barWidth=geometry.module_width_mm * mm,
        barHeight=geometry.height_mm * mm,
        humanReadable=geometry.show_digits,
        quiet=True,
    )
    left, bottom, right, top = widget.getBounds()
    drawing = Drawing(right - left, top - bottom)
    drawing.add(widget)
    return drawing
