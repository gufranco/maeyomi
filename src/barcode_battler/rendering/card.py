"""Draw one card face.

The cards are handled by children, so the face is built around three things a
child can find without reading: a coloured band that says at a glance what the
creature is, three big numbers each behind its own pictogram, and a plain
sentence naming the special power. Everything is laid out in millimetres from
the card edges, so the same code draws a card of any size that will hold one.

The barcode is drawn at a fixed module width and the card is rejected if it
cannot hold one, so nothing above it can squeeze it. Text is wrapped rather
than cut, and only trimmed when it will not fit even after wrapping.
"""

from dataclasses import dataclass
from functools import cache
from typing import Any, Final, cast

from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.geometry import BarcodeGeometry
from barcode_battler.barcode.symbol import draw_symbol, symbol_size_mm
from barcode_battler.models.character import BarcodeBattlerCharacter
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.models.special_ability import UNDOCUMENTED, SpecialAbility
from barcode_battler.rendering.icons import (
    INK,
    RACE_COLOURS,
    RACE_LABELS,
    STAT_STYLES,
    WHITE,
    Colour,
    draw_heart,
    draw_race_icon,
    draw_shield,
    draw_sword,
)

TITLE_FONT: Final = "Helvetica-Bold"
JAPANESE_FONT: Final = "HeiseiKakuGo-W5"
"""A Japanese gothic face for names the Latin fonts have no glyphs for.

It is one of the Adobe Japan1 fonts every PDF reader carries, so it needs no
file here. It is referenced rather than embedded, which is what that font class
is for; see the README on printing official cards.
"""
LATIN_1_LIMIT: Final = 0xFF
BODY_FONT: Final = "Helvetica"
MUTED_INK: Final[Colour] = (0.35, 0.37, 0.43)
PANEL_FILL: Final[Colour] = (0.94, 0.95, 0.96)
MAX_NAME_LINES: Final = 2
MAX_ABILITY_LINES: Final = 3
ELLIPSIS: Final = "..."
SWIPE_CAPTION: Final = "Swipe this end"
SWIPE_SIZE_PT: Final = 6.0
NO_ABILITY: Final = "none"
_PLAIN_ABILITY: Final = {UNDOCUMENTED: "Unknown power", NO_ABILITY: "No special power"}


@dataclass(frozen=True, slots=True)
class CardStyle:
    """Sizes and spacing for one card face, all in millimetres or points."""

    padding_mm: float = 3.6
    band_height_mm: float = 12.5
    name_block_mm: float = 10.5
    stat_block_mm: float = 19.0
    ability_block_mm: float = 12.0
    title_size_pt: float = 13.0
    name_line_mm: float = 5.0
    stat_label_size_pt: float = 7.5
    stat_size_pt: float = 17.0
    band_title_size_pt: float = 9.5
    band_detail_size_pt: float = 7.5
    ability_label_size_pt: float = 6.5
    ability_size_pt: float = 7.5
    ability_line_mm: float = 3.1
    corner_mm: float = 2.4
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
    _draw_band(
        canvas, card, x_mm=x_mm, y_mm=y_mm, width_mm=width_mm, height_mm=height_mm, style=resolved
    )
    cursor = y_mm + height_mm - resolved.band_height_mm
    cursor = _draw_name(canvas, card, x_mm=x_mm, top_mm=cursor, width_mm=width_mm, style=resolved)
    cursor = _draw_stats(canvas, card, x_mm=x_mm, top_mm=cursor, width_mm=width_mm, style=resolved)
    _draw_ability(canvas, card, x_mm=x_mm, top_mm=cursor, width_mm=width_mm, style=resolved)
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
    if resolved.border:
        canvas.setStrokeColorRGB(*MUTED_INK)
        canvas.setLineWidth(0.4)
        canvas.roundRect(
            x_mm * mm, y_mm * mm, width_mm * mm, height_mm * mm, resolved.corner_mm * mm, 1, 0
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
    needed = (
        symbol_height
        + style.band_height_mm
        + style.name_block_mm
        + style.stat_block_mm
        + style.ability_block_mm
        + 2 * style.padding_mm
    )
    if height_mm < needed:
        message = (
            f"card is too short: {height_mm} mm cannot hold a {symbol_height:.2f} mm symbol "
            f"and its text, which need {needed:.2f} mm"
        )
        raise ValueError(message)


def _draw_band(
    canvas: Canvas,
    card: GeneratedCard,
    *,
    x_mm: float,
    y_mm: float,
    width_mm: float,
    height_mm: float,
    style: CardStyle,
) -> None:
    """Fill the top band with the race colour and put the race icon and name on it."""
    colour = RACE_COLOURS[card.character.race]
    band_bottom = y_mm + height_mm - style.band_height_mm
    canvas.saveState()
    canvas.setFillColorRGB(*colour)
    canvas.roundRect(
        x_mm * mm,
        band_bottom * mm,
        width_mm * mm,
        style.band_height_mm * mm,
        style.corner_mm * mm,
        stroke=0,
        fill=1,
    )
    canvas.rect(
        x_mm * mm,
        band_bottom * mm,
        width_mm * mm,
        style.corner_mm * mm,
        stroke=0,
        fill=1,
    )
    canvas.restoreState()

    icon_size = style.band_height_mm - 2 * 1.8
    draw_race_icon(
        canvas,
        card.character.race,
        x_mm=x_mm + style.padding_mm,
        y_mm=band_bottom + 1.8,
        size_mm=icon_size,
    )
    text_left = x_mm + style.padding_mm + icon_size + 2.4
    canvas.setFillColorRGB(*WHITE)
    canvas.setFont(TITLE_FONT, style.band_title_size_pt)
    canvas.drawString(
        text_left * mm,
        (band_bottom + style.band_height_mm / 2 + 0.4) * mm,
        RACE_LABELS[card.character.race],
    )
    canvas.setFont(BODY_FONT, style.band_detail_size_pt)
    canvas.drawString(
        text_left * mm,
        (band_bottom + style.band_height_mm / 2 - 3.2) * mm,
        _role(card.character),
    )


def _role(character: BarcodeBattlerCharacter) -> str:
    """The line under the race: the class for a fighter, the kind for an item."""
    character_class = character.character_class
    if character_class is None:
        return "Item card"
    return character_class.value.title()


def _draw_name(
    canvas: Canvas,
    card: GeneratedCard,
    *,
    x_mm: float,
    top_mm: float,
    width_mm: float,
    style: CardStyle,
) -> float:
    """Draw the name across up to two centred lines, and return the new cursor."""
    available = width_mm - 2 * style.padding_mm
    font = _name_font(card.name)
    lines = _wrap(
        canvas,
        card.name,
        available,
        font=font,
        size_pt=style.title_size_pt,
        max_lines=MAX_NAME_LINES,
    )
    canvas.setFillColorRGB(*INK)
    canvas.setFont(font, style.title_size_pt)
    baseline = top_mm - style.name_line_mm
    for line in lines:
        canvas.drawCentredString((x_mm + width_mm / 2) * mm, baseline * mm, line)
        baseline -= style.name_line_mm
    return top_mm - style.name_block_mm


def _draw_stats(
    canvas: Canvas,
    card: GeneratedCard,
    *,
    x_mm: float,
    top_mm: float,
    width_mm: float,
    style: CardStyle,
) -> float:
    """Draw the three battle numbers as tiles, and return the new cursor."""
    character = card.character
    tiles = (
        ("HP", character.hp, draw_heart),
        ("ST", character.st, draw_sword),
        ("DF", character.df, draw_shield),
    )
    gap = 1.6
    available = width_mm - 2 * style.padding_mm
    tile_width = (available - gap * (len(tiles) - 1)) / len(tiles)
    tile_height = style.stat_block_mm - 2.0
    bottom = top_mm - 1.0 - tile_height
    for index, (label, value, icon) in enumerate(tiles):
        left = x_mm + style.padding_mm + index * (tile_width + gap)
        canvas.saveState()
        canvas.setFillColorRGB(*STAT_STYLES[label].tint)
        canvas.setStrokeColorRGB(*STAT_STYLES[label].icon)
        canvas.setLineWidth(0.4)
        canvas.roundRect(
            left * mm, bottom * mm, tile_width * mm, tile_height * mm, 1.6 * mm, stroke=1, fill=1
        )
        canvas.restoreState()
        icon_size = 5.4
        icon(
            canvas,
            x_mm=left + (tile_width - icon_size) / 2,
            y_mm=bottom + tile_height - icon_size - 1.4,
            size_mm=icon_size,
        )
        canvas.setFillColorRGB(*INK)
        number = str(value)
        canvas.setFont(TITLE_FONT, _fit_size(number, tile_width - 1.6, style.stat_size_pt))
        canvas.drawCentredString((left + tile_width / 2) * mm, (bottom + 4.4) * mm, number)
        canvas.setFillColorRGB(*MUTED_INK)
        canvas.setFont(BODY_FONT, style.stat_label_size_pt)
        canvas.drawCentredString((left + tile_width / 2) * mm, (bottom + 1.2) * mm, label)
    return top_mm - style.stat_block_mm


def _draw_ability(
    canvas: Canvas,
    card: GeneratedCard,
    *,
    x_mm: float,
    top_mm: float,
    width_mm: float,
    style: CardStyle,
) -> None:
    """Draw the special power in a panel, wrapped across as many lines as it needs."""
    available = width_mm - 2 * style.padding_mm
    left = x_mm + style.padding_mm
    height = style.ability_block_mm - 1.0
    bottom = top_mm - height
    canvas.saveState()
    canvas.setFillColorRGB(*PANEL_FILL)
    canvas.roundRect(
        left * mm, bottom * mm, available * mm, height * mm, 1.6 * mm, stroke=0, fill=1
    )
    canvas.restoreState()

    inner = available - 3.0
    canvas.setFillColorRGB(*MUTED_INK)
    canvas.setFont(BODY_FONT, style.ability_label_size_pt)
    canvas.drawString(
        (left + 1.5) * mm,
        (bottom + height - 3.0) * mm,
        f"SPECIAL POWER {card.character.special.code:02d}",
    )
    canvas.setFillColorRGB(*INK)
    canvas.setFont(BODY_FONT, style.ability_size_pt)
    baseline = bottom + height - 6.2
    lines = _wrap(
        canvas,
        _ability_text(card.character.special),
        inner,
        font=BODY_FONT,
        size_pt=style.ability_size_pt,
        max_lines=MAX_ABILITY_LINES,
    )
    for line in lines:
        canvas.drawString((left + 1.5) * mm, baseline * mm, line)
        baseline -= style.ability_line_mm


def _ability_text(special: SpecialAbility) -> str:
    """The ability in words a child can read, rather than the register of a spec.

    The two placeholder descriptions say nothing to a player. Everything else is
    the documented effect and is printed as written, because a card that
    paraphrases the rules is a card that gets them wrong.
    """
    return _PLAIN_ABILITY.get(special.description, special.description)


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
    """Draw the symbol centred at the foot of the card.

    The digits under the bars are drawn by the symbol itself, in the zone the
    standard reserves for them. Printing them a second time would put an
    unrelated line of text inside the quiet zone below the bars.
    """
    symbol_x = x_mm + (width_mm - symbol_width) / 2
    _, symbol_height = draw_symbol(
        canvas, card.barcode, x_mm=symbol_x, y_mm=y_mm + style.padding_mm, geometry=geometry
    )
    canvas.setFillColorRGB(*MUTED_INK)
    canvas.setFont(BODY_FONT, SWIPE_SIZE_PT)
    canvas.drawCentredString(
        (x_mm + width_mm / 2) * mm,
        (y_mm + style.padding_mm + symbol_height + 1.2) * mm,
        SWIPE_CAPTION,
    )


def _wrap(
    canvas: Canvas,
    text: str,
    available_mm: float,
    *,
    font: str,
    size_pt: float,
    max_lines: int,
) -> list[str]:
    """Break text to fit the width, between words or, with no spaces, between characters.

    Japanese is written without spaces, so a name with none is broken between
    characters instead. Text that still does not fit is cut and the cut is
    marked, so a reader can see that a name was shortened rather than reading a
    different name.
    """
    limit = available_mm * mm
    joiner = " " if " " in text.strip() else ""
    tokens = text.split() if joiner else list(text.strip())
    lines: list[str] = []
    current = ""
    truncated = False
    for word in tokens:
        candidate = f"{current}{joiner}{word}" if current else word
        if current and canvas.stringWidth(candidate, font, size_pt) > limit:
            lines.append(current)
            current = word
            if len(lines) == max_lines:
                truncated = True
                current = ""
                break
        else:
            current = candidate
    if current:
        lines.append(current)
    wrapped = [_trim(canvas, line, limit, font, size_pt) for line in lines]
    if truncated and wrapped:
        wrapped[-1] = _cut(canvas, wrapped[-1], limit, font, size_pt)
    return wrapped


def _name_font(name: str) -> str:
    """The face a name is set in: Latin where it can be, Japanese where it must."""
    if all(ord(character) <= LATIN_1_LIMIT for character in name):
        return TITLE_FONT
    _register_japanese_font()
    return JAPANESE_FONT


@cache
def _register_japanese_font() -> None:
    """Register the Japanese face once, the first time a name needs it."""
    cast("Any", pdfmetrics).registerFont(UnicodeCIDFont(JAPANESE_FONT))


def _fit_size(text: str, available_mm: float, size_pt: float) -> float:
    """The largest size up to the preferred one at which the text fits the width."""
    width = pdfmetrics.stringWidth(text, TITLE_FONT, size_pt)
    limit = available_mm * mm
    if width <= limit:
        return size_pt
    return size_pt * limit / width


def _trim(canvas: Canvas, text: str, limit: float, font: str, size_pt: float) -> str:
    """Return the text unchanged when it fits, and cut it when it does not."""
    if canvas.stringWidth(text, font, size_pt) <= limit:
        return text
    return _cut(canvas, text, limit, font, size_pt)


def _cut(canvas: Canvas, text: str, limit: float, font: str, size_pt: float) -> str:
    """Shorten text until it and an ellipsis fit, and mark the cut."""
    trimmed = text
    while trimmed and canvas.stringWidth(trimmed + ELLIPSIS, font, size_pt) > limit:
        trimmed = trimmed[:-1]
    return trimmed + ELLIPSIS
