"""Turn a rendered PDF back into pixels.

The PDF library ships no type information, so every call into it is confined to
this module and given an explicit type at the boundary. Everything downstream
works with typed images. PDFium is not thread-safe, and the server draws on a
pool of threads, so one lock lets a single render run at a time; two at once
corrupt PDFium's heap and kill the process.
"""

from pathlib import Path
from threading import Lock
from typing import Any, Final, cast

import pypdfium2 as pdfium
from PIL import ImageChops
from PIL.Image import Image

PDF_POINTS_PER_INCH: Final = 72
PDFIUM: Final = Lock()


def render_pdf_pages(path: str | Path, *, dpi: int) -> list[Image]:
    """Render every page of a PDF at the given resolution, one render at a time."""
    with PDFIUM:
        document = cast("Any", pdfium.PdfDocument(str(path)))
        try:
            scale = dpi / PDF_POINTS_PER_INCH
            return [
                cast("Image", document[index].render(scale=scale).to_pil().copy())
                for index in range(len(document))
            ]
        finally:
            document.close()


def ink_box(image: Image) -> tuple[int, int, int, int] | None:
    """Return the bounding box of everything drawn on a white page, or None if blank."""
    inverted = ImageChops.invert(image.convert("L"))
    return inverted.getbbox()
