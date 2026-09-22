"""Tests for exporting a rendered sheet to raster images."""

from pathlib import Path

import pytest
from PIL import Image

from barcode_battler.barcode.verify import decode_image
from barcode_battler.decoder.decode import decode
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.rendering.export import ImageFormat, export_images
from barcode_battler.rendering.sheet import write_sheet

BARCODE = "0401207237501"


def sheet(path: Path, count: int = 2) -> None:
    card = GeneratedCard(name="Fire Knight", barcode=BARCODE, character=decode(BARCODE))
    write_sheet([card] * count, path)


def test_one_image_is_written_per_page(tmp_path: Path) -> None:
    pdf = tmp_path / "sheet.pdf"
    sheet(pdf)

    images = export_images(pdf, tmp_path / "out", image_format=ImageFormat.PNG)

    assert len(images) == 1
    assert images[0].exists()


@pytest.mark.parametrize("image_format", list(ImageFormat))
def test_every_supported_format_is_written(tmp_path: Path, image_format: ImageFormat) -> None:
    pdf = tmp_path / "sheet.pdf"
    sheet(pdf)

    images = export_images(pdf, tmp_path / image_format.value, image_format=image_format)

    assert images[0].suffix == f".{image_format.value}"
    assert images[0].stat().st_size > 0


def test_an_exported_image_still_carries_a_scannable_barcode(tmp_path: Path) -> None:
    pdf = tmp_path / "sheet.pdf"
    sheet(pdf, count=1)

    images = export_images(pdf, tmp_path / "out", image_format=ImageFormat.PNG)

    with Image.open(images[0]) as opened:
        assert decode_image(opened.convert("RGB")) == [BARCODE]


def test_the_resolution_is_honoured(tmp_path: Path) -> None:
    pdf = tmp_path / "sheet.pdf"
    sheet(pdf, count=1)

    low = export_images(pdf, tmp_path / "low", image_format=ImageFormat.PNG, dpi=150)
    high = export_images(pdf, tmp_path / "high", image_format=ImageFormat.PNG, dpi=300)

    with Image.open(low[0]) as small, Image.open(high[0]) as large:
        assert large.width == pytest.approx(small.width * 2, abs=2)


def test_pages_are_numbered_from_one(tmp_path: Path) -> None:
    pdf = tmp_path / "sheet.pdf"
    write_sheet([GeneratedCard(name="x", barcode=BARCODE, character=decode(BARCODE))] * 10, pdf)

    images = export_images(pdf, tmp_path / "out", image_format=ImageFormat.PNG, dpi=72)

    assert [path.stem for path in images] == ["page-01", "page-02"]
