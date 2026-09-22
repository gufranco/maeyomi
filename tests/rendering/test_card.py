"""Tests for one card face."""

from pathlib import Path

import pypdfium2 as pdfium
import pytest
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.geometry import BarcodeGeometry
from barcode_battler.barcode.rasterise import render_pdf_pages
from barcode_battler.barcode.verify import decode_image, decode_pdf
from barcode_battler.decoder.decode import decode
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.rendering.card import CardStyle, draw_card
from barcode_battler.rendering.layout import POKER_CARD_HEIGHT_MM, POKER_CARD_WIDTH_MM

BARCODE = "0401207237501"


def sample(name: str = "Fire Knight") -> GeneratedCard:
    return GeneratedCard(name=name, barcode=BARCODE, character=decode(BARCODE))


def render(
    path: Path,
    card: GeneratedCard,
    *,
    width: float = POKER_CARD_WIDTH_MM,
    height: float = POKER_CARD_HEIGHT_MM,
    style: CardStyle | None = None,
) -> None:
    canvas = Canvas(str(path), pagesize=(width * mm, height * mm))
    draw_card(
        canvas,
        card,
        x_mm=0,
        y_mm=0,
        width_mm=width,
        height_mm=height,
        geometry=BarcodeGeometry(),
        style=style,
    )
    canvas.showPage()
    canvas.save()


def test_a_card_renders_a_scannable_barcode(tmp_path: Path) -> None:
    path = tmp_path / "card.pdf"

    render(path, sample())

    assert decode_pdf(path) == [BARCODE]


def test_the_card_prints_its_name_and_stats(tmp_path: Path) -> None:
    path = tmp_path / "text.pdf"

    render(path, sample())

    text = pdf_text(path)
    assert "Fire Knight" in text
    for label, value in (("HP", "4000"), ("ST", "1200"), ("DF", "700")):
        assert label in text
        assert value in text


def test_the_card_prints_race_class_and_ability(tmp_path: Path) -> None:
    path = tmp_path / "detail.pdf"

    render(path, sample())

    text = pdf_text(path)
    assert "Race: Aquatic" in text
    assert "Class: Warrior" in text
    assert "Ability: 50" in text


def test_the_card_prints_the_numeric_code(tmp_path: Path) -> None:
    path = tmp_path / "digits.pdf"

    render(path, sample())

    assert BARCODE in pdf_text(path)


def test_a_long_name_is_trimmed_rather_than_overflowing(tmp_path: Path) -> None:
    path = tmp_path / "long.pdf"

    render(path, sample("A" * 200))

    assert "..." in pdf_text(path)


def test_a_card_too_narrow_for_its_symbol_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="too narrow"):
        render(tmp_path / "narrow.pdf", sample(), width=30.0)


def test_a_card_too_short_for_its_symbol_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="too short"):
        render(tmp_path / "short.pdf", sample(), height=30.0)


def test_the_border_can_be_turned_off(tmp_path: Path) -> None:
    bordered = tmp_path / "bordered.pdf"
    plain = tmp_path / "plain.pdf"

    render(bordered, sample(), style=CardStyle(border=True))
    render(plain, sample(), style=CardStyle(border=False))

    assert bordered.stat().st_size != plain.stat().st_size


def test_the_symbol_sits_inside_the_card(tmp_path: Path) -> None:
    path = tmp_path / "inside.pdf"

    render(path, sample())

    image = render_pdf_pages(path, dpi=300)[0]
    assert decode_image(image) == [BARCODE]


def pdf_text(path: Path) -> str:
    document = pdfium.PdfDocument(str(path))
    try:
        return str(document[0].get_textpage().get_text_range())
    finally:
        document.close()
