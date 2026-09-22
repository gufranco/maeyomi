"""Draw one card face.

The layout is deliberately plain: a name, the three numbers a player reads
during a battle, the three categorical fields, then the symbol and its digits.
The barcode is drawn at a fixed module width and the card is rejected if it
cannot hold one, so nothing above it can squeeze it.
"""

from dataclasses import dataclass
from typing import Final

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.geometry import BarcodeGeometry
from barcode_battler.barcode.symbol import draw_symbol, symbol_size_mm
from barcode_battler.models.generated_card import GeneratedCard

TITLE_FONT: Final = "Helvetica-Bold"
BODY_FONT: Final = "Helvetica"
DIGITS_FONT: Final = "Courier"
_TEXT_LINES_ABOVE_SYMBOL: Final = 8


@dataclass(frozen=True, slots=True)
class CardStyle:
    """Type sizes and spacing for one card face."""

    padding_mm: float = 4.0
    title_size_pt: float = 11.0
    stat_size_pt: float = 10.0
    detail_size_pt: float = 7.5
    digits_size_pt: float = 7.0
    line_spacing_mm: float = 4.6
    border: bool = True


def draw_card(
    canvas: Canvas,
    card: GeneratedCard,
    *,
    x_mm: float,
    y_mm: float,
    width_mm: float,
    height_mm: float,
    geometry: BarcodeGeometry,
    style: CardStyle | None = None,
) -> None:
    """Draw one card with its lower left corner at the given point."""
    resolved = style or CardStyle()
    symbol_width, symbol_height = symbol_size_mm(card.barcode, geometry)
    _check_fits(width_mm, height_mm, symbol_width, symbol_height, resolved)
    if resolved.border:
        canvas.setLineWidth(0.25)
        canvas.rect(x_mm * mm, y_mm * mm, width_mm * mm, height_mm * mm)
    _draw_text(
        canvas, card, x_mm=x_mm, y_mm=y_mm, width_mm=width_mm, height_mm=height_mm, style=resolved
    )
    _draw_barcode(
        canvas,
        card,
        x_mm=x_mm,
        y_mm=y_mm,
        width_mm=width_mm,
        symbol_width=symbol_width,
        geometry=geometry,
        style=resolved,
    )


def _check_fits(
    width_mm: float,
    height_mm: float,
    symbol_width: float,
    symbol_height: float,
    style: CardStyle,
) -> None:
    """Reject a card that cannot hold its own barcode at the required module width."""
    if width_mm < symbol_width + 2 * style.padding_mm:
        message = (
            f"card is too narrow: {width_mm} mm cannot hold a {symbol_width:.2f} mm symbol "
            f"plus {style.padding_mm} mm of padding on each side"
        )
        raise ValueError(message)
    needed = symbol_height + _TEXT_LINES_ABOVE_SYMBOL * style.line_spacing_mm + 2 * style.padding_mm
    if height_mm < needed:
        message = (
            f"card is too short: {height_mm} mm cannot hold a {symbol_height:.2f} mm symbol "
            f"and its text, which need {needed:.2f} mm"
        )
        raise ValueError(message)


def _draw_text(
    canvas: Canvas,
    card: GeneratedCard,
    *,
    x_mm: float,
    y_mm: float,
    width_mm: float,
    height_mm: float,
    style: CardStyle,
) -> None:
    """Draw the name, the three stats and the three categorical fields."""
    left = x_mm + style.padding_mm
    available = width_mm - 2 * style.padding_mm
    cursor = y_mm + height_mm - style.padding_mm - style.line_spacing_mm
    canvas.setFont(TITLE_FONT, style.title_size_pt)
    title = _clip(canvas, card.name, available, TITLE_FONT, style.title_size_pt)
    canvas.drawString(left * mm, cursor * mm, title)
    cursor -= style.line_spacing_mm * 1.4

    character = card.character
    canvas.setFont(BODY_FONT, style.stat_size_pt)
    for label, value in (("HP", character.hp), ("ST", character.st), ("DF", character.df)):
        canvas.drawString(left * mm, cursor * mm, f"{label}: {value}")
        cursor -= style.line_spacing_mm

    cursor -= style.line_spacing_mm * 0.3
    canvas.setFont(BODY_FONT, style.detail_size_pt)
    for line in _detail_lines(card):
        clipped = _clip(canvas, line, available, BODY_FONT, style.detail_size_pt)
        canvas.drawString(left * mm, cursor * mm, clipped)
        cursor -= style.line_spacing_mm * 0.85


def _detail_lines(card: GeneratedCard) -> list[str]:
    """The race, class and ability lines shown under the stats."""
    character = card.character
    character_class = character.character_class
    return [
        f"Race: {_title(character.race.name)}",
        f"Class: {_title(character_class.value) if character_class else 'Item'}",
        f"Ability: {character.special.code:02d} {character.special.description}",
    ]


def _clip(canvas: Canvas, text: str, available_mm: float, font: str, size_pt: float) -> str:
    """Trim text that would overflow the card, marking the trim with an ellipsis."""
    limit = available_mm * mm
    if canvas.stringWidth(text, font, size_pt) <= limit:
        return text
    trimmed = text
    while trimmed and canvas.stringWidth(trimmed + "...", font, size_pt) > limit:
        trimmed = trimmed[:-1]
    return trimmed + "..."


def _title(value: str) -> str:
    """Render an enum name as readable text."""
    return value.replace("_", " ").title()


def _draw_barcode(
    canvas: Canvas,
    card: GeneratedCard,
    *,
    x_mm: float,
    y_mm: float,
    width_mm: float,
    symbol_width: float,
    geometry: BarcodeGeometry,
    style: CardStyle,
) -> None:
    """Draw the symbol centred near the foot of the card, with its digits beneath."""
    symbol_x = x_mm + (width_mm - symbol_width) / 2
    digits_baseline = y_mm + style.padding_mm
    symbol_y = digits_baseline + style.line_spacing_mm
    draw_symbol(canvas, card.barcode, x_mm=symbol_x, y_mm=symbol_y, geometry=geometry)
    canvas.setFont(DIGITS_FONT, style.digits_size_pt)
    canvas.drawCentredString((x_mm + width_mm / 2) * mm, digits_baseline * mm, card.barcode)
