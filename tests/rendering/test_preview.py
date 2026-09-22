"""Tests for the on-screen preview.

The preview is the print renderer rasterised, not a second drawing of the same
card, so what the screen shows and what the printer produces cannot drift
apart. These tests assert that by decoding the preview image.
"""

import io

import pytest
from PIL import Image

from barcode_battler.barcode.verify import decode_image
from barcode_battler.decoder.decode import decode
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.rendering.layout import CARD_HEIGHT_MM, CARD_WIDTH_MM
from barcode_battler.rendering.preview import card_png, sheet_png_pages

BARCODE = "0401207237501"


def sample(name: str = "Fire Knight") -> GeneratedCard:
    return GeneratedCard(name=name, barcode=BARCODE, character=decode(BARCODE))


def opened(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def test_a_card_preview_is_a_png() -> None:
    data = card_png(sample())

    assert data[:8] == b"\x89PNG\r\n\x1a\n"


def test_a_card_preview_carries_a_scannable_barcode() -> None:
    with opened(card_png(sample(), dpi=300)) as image:
        assert decode_image(image.convert("RGB")) == [BARCODE]


def test_a_card_preview_has_the_aspect_ratio_of_the_printed_card() -> None:
    with opened(card_png(sample())) as image:
        ratio = image.width / image.height

    assert ratio == pytest.approx(CARD_WIDTH_MM / CARD_HEIGHT_MM, abs=0.02)


def test_a_higher_resolution_preview_is_larger() -> None:
    with (
        opened(card_png(sample(), dpi=100)) as small,
        opened(card_png(sample(), dpi=200)) as large,
    ):
        assert large.width == pytest.approx(small.width * 2, abs=2)


def test_a_sheet_preview_returns_one_image_per_page() -> None:
    pages = sheet_png_pages([sample()] * 10)

    assert len(pages) == 2
    assert all(page[:8] == b"\x89PNG\r\n\x1a\n" for page in pages)


def test_a_sheet_preview_carries_every_barcode() -> None:
    pages = sheet_png_pages([sample()] * 3, dpi=300)

    with opened(pages[0]) as image:
        assert decode_image(image.convert("RGB")) == [BARCODE] * 3


def test_an_empty_sheet_preview_has_no_pages() -> None:
    assert sheet_png_pages([]) == []


def test_a_card_too_small_for_its_barcode_is_rejected() -> None:
    with pytest.raises(ValueError, match="too narrow"):
        card_png(sample(), width_mm=30.0, height_mm=40.0)
