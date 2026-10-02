"""Draw an EAN symbol as vectors at an exact module width.

ReportLab's EAN widgets are used rather than a rasterised image, because a
raster scaled to fit a layout rounds its module widths unevenly, which is a
scan failure that no test on the digit string would catch. The module width is
set explicitly and the symbol's size follows from it.

Quiet zones come from the widget's own `quiet` flag rather than from explicit
values, because its `lquiet` and `rquiet` attributes are declared as booleans
and reject a length. The width it produces is measured against the standard in
`test_symbol.py` rather than assumed.

The widget's `barHeight` is the guard bar height, not the data bar height: the
data bars are shorter by the zone the digits sit in. The geometry is therefore
asked for its drawn height, which already includes that zone, and the tests
measure the data bars off a rendered page rather than trusting the setting to
reach them.
"""

import re
from typing import Final

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.eanbc import Ean8BarcodeWidget, Ean13BarcodeWidget
from reportlab.graphics.barcode.widgets import BarcodeCode128, BarcodeStandard39
from reportlab.graphics.shapes import Drawing
from reportlab.lib.attrmap import AttrMap, AttrMapValue
from reportlab.lib.units import mm
from reportlab.lib.validators import isString
from reportlab.pdfgen.canvas import Canvas

from maeyomi.barcode.geometry import (
    EAN_8_LENGTH,
    EAN_13_LENGTH,
    QUIET_MODULES,
    BarcodeGeometry,
    Symbology,
)
from maeyomi.barcode.stripes import stripes_size_mm
from maeyomi.decoder.errors import (
    InvalidCharacterError,
    InvalidLengthError,
    UnsupportedBarcodeError,
)
from maeyomi.decoder.validation import validate_barcode
from maeyomi.said import Said

_WIDGETS: Final = {EAN_13_LENGTH: Ean13BarcodeWidget, EAN_8_LENGTH: Ean8BarcodeWidget}
CODE39_CHARACTERS: Final = re.compile(r"[0-9A-Z\-. $/+%]+")
CODE39_FRAME: Final = "*"
CODE39_RATIO: Final = 2.5
CODE39_ONLY: Final = Said(
    "Code 39 carries only capital letters, digits and - . space $ / + %",
    "Code 39 に つかえるのは おおもじの アルファベット、すうじ、- . スペース $ / + % だけ",
)


class KeptCheckEan13(Ean13BarcodeWidget):
    """An EAN-13 that draws the thirteenth digit it is given instead of working one out."""

    _attrMap = AttrMap(BASE=Ean13BarcodeWidget, drawn_check_digit=AttrMapValue(isString))  # noqa: N815
    drawn_check_digit: str = "0"

    def _checkdigit(self, _num: str) -> str:
        """The digit the code arrived with, whatever the other twelve add up to."""
        return self.drawn_check_digit


def symbol_size_mm(code: str, geometry: BarcodeGeometry) -> tuple[float, float]:
    """Return the width and height in millimetres the drawn symbol occupies."""
    if geometry.symbology is Symbology.STRIPES:
        return stripes_size_mm(code)
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
    widget = _widget(code, geometry)
    left, bottom, right, top = widget.getBounds()
    drawing = Drawing(right - left, top - bottom)
    drawing.add(widget)
    return drawing


def _widget(
    code: str, geometry: BarcodeGeometry
) -> Ean13BarcodeWidget | BarcodeStandard39 | BarcodeCode128:
    """The widget the geometry's symbology draws the code with."""
    if geometry.symbology is Symbology.CODE39:
        return code39_widget(code, geometry)
    if geometry.symbology is Symbology.CODE128:
        return code128_widget(code, geometry)
    return kept_widget(code, geometry) if geometry.kept_check else _checked_widget(code, geometry)


def code39_widget(code: str, geometry: BarcodeGeometry) -> BarcodeStandard39:
    """A Code 39 symbol for the text, framed by its start and stop characters."""
    text = code.strip(CODE39_FRAME)
    if not CODE39_CHARACTERS.fullmatch(text):
        raise UnsupportedBarcodeError(barcode=code, reason=CODE39_ONLY)
    return BarcodeStandard39(
        value=text, ratio=CODE39_RATIO, checksum=0, stop=1, **_linear_sizes(geometry)
    )


def code128_widget(code: str, geometry: BarcodeGeometry) -> BarcodeCode128:
    """A Code 128 symbol for an even run of digits, which it carries as pairs."""
    if not code.isdigit():
        raise InvalidCharacterError(barcode=code)
    if len(code) % 2:
        raise InvalidLengthError(length=len(code))
    return BarcodeCode128(value=code, **_linear_sizes(geometry))


def _linear_sizes(geometry: BarcodeGeometry) -> dict[str, float | bool]:
    """The settings a Code 39 or Code 128 widget takes from the geometry."""
    module = geometry.module_width_mm * mm
    return {
        "barWidth": module,
        "barHeight": geometry.bar_height_mm * mm,
        "humanReadable": geometry.show_digits,
        "quiet": True,
        "lquiet": QUIET_MODULES * module,
        "rquiet": QUIET_MODULES * module,
    }


def _checked_widget(code: str, geometry: BarcodeGeometry) -> Ean13BarcodeWidget:
    """The widget for a code whose check digit must be right."""
    normalised = validate_barcode(code)
    return _WIDGETS[len(normalised)](normalised, **_sizes(geometry))


def kept_widget(code: str, geometry: BarcodeGeometry) -> Ean13BarcodeWidget:
    """The widget for thirteen digits drawn exactly as given, check digit included."""
    if not code.isdigit():
        raise InvalidCharacterError(barcode=code)
    if len(code) != EAN_13_LENGTH:
        raise InvalidLengthError(length=len(code))
    widget = KeptCheckEan13(code[:-1], **_sizes(geometry))
    widget.drawn_check_digit = code[-1]
    return widget


def _sizes(geometry: BarcodeGeometry) -> dict[str, float | bool]:
    """The widget settings the geometry fixes."""
    return {
        "barWidth": geometry.module_width_mm * mm,
        "barHeight": geometry.drawn_height_mm * mm,
        "humanReadable": geometry.show_digits,
        "quiet": True,
    }
