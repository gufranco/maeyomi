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
    assert "Sea creature" in text
    assert "Warrior" in text
    assert "hero flag" in text


def test_the_card_prints_the_numeric_code(tmp_path: Path) -> None:
    path = tmp_path / "digits.pdf"

    render(path, sample())

    assert "0 401207 237501" in pdf_text(path)


def test_the_numeric_code_is_printed_once(tmp_path: Path) -> None:
    path = tmp_path / "once.pdf"

    render(path, sample())

    assert pdf_text(path).count("237501") == 1


def test_a_long_name_wraps_onto_a_second_line(tmp_path: Path) -> None:
    path = tmp_path / "long.pdf"

    render(path, sample("Thunder Dragon of the Northern Peaks"))

    text = pdf_text(path)
    assert "Thunder" in text
    assert "Peaks" in text


def test_a_name_too_long_to_wrap_is_trimmed_rather_than_overflowing(tmp_path: Path) -> None:
    path = tmp_path / "huge.pdf"

    render(path, sample("A" * 400))

    assert "..." in pdf_text(path)


def test_a_long_ability_wraps_instead_of_being_cut(tmp_path: Path) -> None:
    path = tmp_path / "ability.pdf"
    barcode = "0501209100305"
    card = GeneratedCard(name="Trickster", barcode=barcode, character=decode(barcode))

    render(path, card)

    text = pdf_text(path)
    assert card.character.special.description.split()[-1] in text
    assert "..." not in text


def test_nothing_is_drawn_over_the_symbol(tmp_path: Path) -> None:
    path = tmp_path / "clear.pdf"

    render(path, sample("Thunder Dragon of the Northern Peaks"))

    assert decode_image(render_pdf_pages(path, dpi=300)[0]) == [BARCODE]


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


def test_an_undocumented_ability_is_named_in_plain_words(tmp_path: Path) -> None:
    path = tmp_path / "unknown.pdf"
    barcode = "0221219400645"
    card = GeneratedCard(name="Mystery", barcode=barcode, character=decode(barcode))

    render(path, card)

    text = pdf_text(path)
    assert "undocumented" not in text
    assert "Unknown power" in text


def test_a_card_with_no_ability_says_so_in_plain_words(tmp_path: Path) -> None:
    path = tmp_path / "none.pdf"
    barcode = "0392110470003"
    card = GeneratedCard(name="Pip", barcode=barcode, character=decode(barcode))

    render(path, card)

    assert "No special power" in pdf_text(path)


def test_the_card_tells_a_child_which_end_to_swipe(tmp_path: Path) -> None:
    path = tmp_path / "swipe.pdf"

    render(path, sample())

    assert "Swipe this end" in pdf_text(path)


def test_an_item_card_says_it_is_an_item_rather_than_naming_a_class(tmp_path: Path) -> None:
    path = tmp_path / "item.pdf"
    barcode = "0000021600005"
    card = GeneratedCard(name="Sharp Stick", barcode=barcode, character=decode(barcode))

    render(path, card)

    text = pdf_text(path)
    assert "Item card" in text
    assert "Weapon, one use" in text


def test_a_name_longer_than_two_lines_is_cut_on_the_second(tmp_path: Path) -> None:
    path = tmp_path / "overflow.pdf"
    name = "The Extremely Enormous Thundering Dragon King of the Far Northern Mountain Peaks"

    render(path, sample(name))

    text = pdf_text(path)
    assert "..." in text
    assert "Peaks" not in text


def test_a_japanese_name_is_printed_in_a_font_that_has_its_glyphs(tmp_path: Path) -> None:
    path = tmp_path / "japanese.pdf"

    render(path, sample("甲賀の巻物"))

    assert "甲賀の巻物" in pdf_text(path)


def test_a_long_japanese_name_breaks_between_characters(tmp_path: Path) -> None:
    path = tmp_path / "long-japanese.pdf"
    name = "外伝最後の死闘黒魔術王パノラマンダー大王"

    render(path, sample(name))

    text = pdf_text(path).replace("\r\n", "")
    assert name in text


def test_the_largest_numbers_the_device_holds_are_printed_whole(tmp_path: Path) -> None:
    path = tmp_path / "huge.pdf"
    barcode = "9994599095183"
    card = GeneratedCard(name="Maximus", barcode=barcode, character=decode(barcode))

    render(path, card)

    text = pdf_text(path)
    for value in ("99900", "24500", "19900"):
        assert value in text


def test_one_word_wider_than_the_card_is_cut_on_its_own_line(tmp_path: Path) -> None:
    path = tmp_path / "wide-word.pdf"

    render(path, sample("Sir " + "Supercalifragilistic" * 3))

    text = pdf_text(path)
    assert "Sir" in text
    assert "..." in text
