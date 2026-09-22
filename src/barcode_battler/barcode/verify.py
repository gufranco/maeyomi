"""Read a rendered barcode back out of the page it was drawn on.

A digit-level test says nothing about whether a scanner can read the ink. Every
rendered page is rasterised and decoded here, and the decoded digits are
compared against the digits the page was supposed to carry.
"""

from pathlib import Path
from typing import Any, cast

import zxingcpp
from PIL.Image import Image

from barcode_battler.barcode.geometry import PRINT_DPI
from barcode_battler.barcode.rasterise import render_pdf_pages


def decode_image(image: Image) -> list[str]:
    """Return the digits of every valid barcode found in an image."""
    results = cast("list[Any]", zxingcpp.read_barcodes(image))
    return [str(result.text) for result in results if result.valid]


def decode_pdf(path: str | Path, *, dpi: int = PRINT_DPI) -> list[str]:
    """Rasterise every page of a PDF and return the digits of every barcode found."""
    found: list[str] = []
    for image in render_pdf_pages(path, dpi=dpi):
        found += decode_image(image)
    return found
