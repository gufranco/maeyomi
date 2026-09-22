"""Export a rendered sheet to raster images.

Images are produced by rasterising the PDF, not by a second renderer, so an
exported page has the same geometry as the page that was verified.
"""

from enum import Enum
from pathlib import Path
from typing import Final

from maeyomi.barcode.geometry import PRINT_DPI
from maeyomi.barcode.rasterise import render_pdf_pages


class ImageFormat(Enum):
    """A raster format a sheet can be exported to."""

    PNG = "png"
    JPEG = "jpg"
    WEBP = "webp"


_PILLOW_FORMATS: Final = {
    ImageFormat.PNG: "PNG",
    ImageFormat.JPEG: "JPEG",
    ImageFormat.WEBP: "WEBP",
}


def export_images(
    pdf_path: str | Path,
    out_dir: str | Path,
    *,
    image_format: ImageFormat = ImageFormat.PNG,
    dpi: int = PRINT_DPI,
) -> list[Path]:
    """Write one image per page and return the paths, in page order."""
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for number, image in enumerate(render_pdf_pages(pdf_path, dpi=dpi), start=1):
        path = directory / f"page-{number:02d}.{image_format.value}"
        image.convert("RGB").save(path, _PILLOW_FORMATS[image_format])
        written.append(path)
    return written
