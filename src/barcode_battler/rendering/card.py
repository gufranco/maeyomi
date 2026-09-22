"""Draw one card face, in English and Japanese, with a picture for every fact.

The cards are handled by children, some of whom read English, some Japanese and
some neither yet. So every fact on the face is said three ways: in English, in
Japanese, and as a picture. A coloured band with a pictogram says what the
creature is. Three tiles with a heart, a sword and a shield carry the battle
numbers. A pictogram beside the special power shows what it changes and which
way.

Everything is laid out in millimetres from the card edges, so the same code draws
a card of any size that will hold one. The barcode is drawn at a fixed module
width and the card is rejected if it cannot hold one, so nothing above it can
squeeze it. The name takes one line when it fits and two when it does not, and
the special power gets whatever height the name leaves.
"""

from dataclasses import dataclass
from typing import Final

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.geometry import BarcodeGeometry
from barcode_battler.barcode.symbol import draw_symbol, symbol_size_mm
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.rendering.ability_icons import draw_ability_icon
from barcode_battler.rendering.icons import (
    INK,
    RACE_COLOURS,
    STAT_STYLES,
    WHITE,
    Colour,
    draw_heart,
    draw_race_icon,
    draw_shield,
    draw_sword,
)
from barcode_battler.rendering.labels import (
    SPECIAL_POWER,
    STAT_LABELS,
    SWIPE,
    Bilingual,
    ability_text,
    class_label,
    race_label,
)
from barcode_battler.rendering.text import fit_size, font_for, text_width_mm, wrap

MUTED_INK: Final[Colour] = (0.35, 0.37, 0.43)
PANEL_FILL: Final[Colour] = (0.94, 0.95, 0.96)
MAX_NAME_LINES: Final = 2
PAIR_GAP_MM: Final = 1.6
SWIPE_GAP_MM: Final = 2.4


@dataclass(frozen=True, slots=True)
class CardStyle:
    """Sizes and spacing for one card face, in millimetres and points."""

    padding_mm: float = 4.0
    band_height_mm: float = 11.5
    stat_block_mm: float = 15.0
    min_ability_block_mm: float = 10.5
    block_gap_mm: float = 0.8
    swipe_block_mm: float = 2.8
    title_size_pt: float = 12.0
    name_line_mm: float = 4.5
    band_title_size_pt: float = 9.0
    band_detail_size_pt: float = 7.0
    stat_size_pt: float = 15.0
    stat_label_size_pt: float = 5.5
    stat_icon_mm: float = 4.6
    ability_icon_mm: float = 8.0
    ability_label_size_pt: float = 5.5
    ability_size_pt: float = 6.5
    ability_line_mm: float = 2.75
    swipe_size_pt: float = 5.5
    corner_mm: float = 2.4
    border: bool = True


@dataclass(frozen=True, slots=True)
class _Frame:
    """Where the card sits on the page."""

    x: float
    y: float
    width: float
    height: float
    style: CardStyle

    @property
    def inner_left(self) -> float:
        """The left edge of the padded content area."""
        return self.x + self.style.padding_mm

    @property
    def inner_width(self) -> float:
        """The width of the padded content area."""
        return self.width - 2 * self.style.padding_mm

    @property
    def centre(self) -> float:
        """The vertical centre line of the card."""
        return self.x + self.width / 2


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
    bleed_mm: float = 0.0,
) -> None:
    """Draw one card with its lower left corner at the given point.

    `bleed_mm` extends the background past the trim line on every side, so a cut
    that lands a fraction off still finds ink rather than white paper.
    """
    frame = _Frame(x_mm, y_mm, width_mm, height_mm, style or CardStyle())
    symbol_width, symbol_height = symbol_size_mm(card.barcode, geometry)
    _check_fits(frame, symbol_width, symbol_height)
    if bleed_mm > 0:
        _draw_bleed(canvas, card, frame, bleed_mm)
    _draw_band(canvas, card, frame)
    bottom_of_text = _draw_barcode(canvas, card, frame, symbol_width, geometry)
    content = frame
    cursor = frame.y + frame.height - frame.style.band_height_mm - frame.style.block_gap_mm
    cursor = _draw_name(canvas, card, content, cursor)
    cursor = _draw_stats(canvas, card, content, cursor)
    _draw_ability(canvas, card, content, top=cursor, bottom=bottom_of_text)
    if frame.style.border:
        canvas.setStrokeColorRGB(*MUTED_INK)
        canvas.setLineWidth(0.4)
        canvas.roundRect(
            x_mm * mm, y_mm * mm, width_mm * mm, height_mm * mm, frame.style.corner_mm * mm, 1, 0
        )


def _draw_bleed(canvas: Canvas, card: GeneratedCard, frame: _Frame, bleed: float) -> None:
    """Paint the card's background past the trim line on every side."""
    style = frame.style
    canvas.saveState()
    canvas.setFillColorRGB(*WHITE)
    canvas.rect(
        (frame.x - bleed) * mm,
        (frame.y - bleed) * mm,
        (frame.width + 2 * bleed) * mm,
        (frame.height + 2 * bleed) * mm,
        stroke=0,
        fill=1,
    )
    canvas.setFillColorRGB(*RACE_COLOURS[card.character.race])
    canvas.rect(
        (frame.x - bleed) * mm,
        (frame.y + frame.height - style.band_height_mm) * mm,
        (frame.width + 2 * bleed) * mm,
        (style.band_height_mm + bleed) * mm,
        stroke=0,
        fill=1,
    )
    canvas.restoreState()


def _check_fits(frame: _Frame, symbol_width: float, symbol_height: float) -> None:
    """Reject a card that cannot hold its own barcode at the required module width."""
    style = frame.style
    if frame.width < symbol_width + 2 * style.padding_mm:
        message = (
            f"card is too narrow: {frame.width} mm cannot hold a {symbol_width:.2f} mm "
            f"symbol plus {style.padding_mm} mm of padding on each side"
        )
        raise ValueError(message)
    needed = (
        style.padding_mm
        + symbol_height
        + style.swipe_block_mm
        + style.min_ability_block_mm
        + style.stat_block_mm
        + MAX_NAME_LINES * style.name_line_mm
        + style.band_height_mm
        + 3 * style.block_gap_mm
    )
    if frame.height < needed:
        message = (
            f"card is too short: {frame.height} mm cannot hold a {symbol_height:.2f} mm "
            f"symbol and its text, which need {needed:.2f} mm"
        )
        raise ValueError(message)


def _draw_band(canvas: Canvas, card: GeneratedCard, frame: _Frame) -> None:
    """Fill the top band with the race colour, and name the kind of card on it."""
    style = frame.style
    race = card.character.race
    band_bottom = frame.y + frame.height - style.band_height_mm
    canvas.saveState()
    canvas.setFillColorRGB(*RACE_COLOURS[race])
    canvas.roundRect(
        frame.x * mm,
        band_bottom * mm,
        frame.width * mm,
        style.band_height_mm * mm,
        style.corner_mm * mm,
        stroke=0,
        fill=1,
    )
    canvas.rect(
        frame.x * mm, band_bottom * mm, frame.width * mm, style.corner_mm * mm, stroke=0, fill=1
    )
    canvas.restoreState()

    inset = 1.8
    icon_size = style.band_height_mm - 2 * inset
    draw_race_icon(canvas, race, x_mm=frame.inner_left, y_mm=band_bottom + inset, size_mm=icon_size)
    text_left = frame.inner_left + icon_size + 2.2
    available = frame.x + frame.width - style.padding_mm - text_left
    middle = band_bottom + style.band_height_mm / 2
    canvas.setFillColorRGB(*WHITE)
    _draw_pair(
        canvas,
        race_label(race),
        x=text_left,
        baseline=middle + 0.5,
        size_pt=style.band_title_size_pt,
        available=available,
        bold=True,
    )
    _draw_pair(
        canvas,
        class_label(card.character.character_class),
        x=text_left,
        baseline=middle - 3.4,
        size_pt=style.band_detail_size_pt,
        available=available,
    )


def _draw_pair(
    canvas: Canvas,
    text: Bilingual,
    *,
    x: float,
    baseline: float,
    size_pt: float,
    available: float,
    bold: bool = False,
    centred: bool = False,
    gap: float = PAIR_GAP_MM,
) -> None:
    """Set the English and then the Japanese on one line, shrinking both to fit.

    With `centred` the pair is centred on `x`; otherwise it starts there.
    """
    english_font = font_for(text.english, bold=bold)
    japanese_font = font_for(text.japanese, bold=bold)
    natural = (
        text_width_mm(text.english, english_font, size_pt)
        + gap
        + text_width_mm(text.japanese, japanese_font, size_pt)
    )
    scale = min(1.0, available / natural)
    size = size_pt * scale
    left = x - natural * scale / 2 if centred else x
    canvas.setFont(english_font, size)
    canvas.drawString(left * mm, baseline * mm, text.english)
    japanese_left = left + text_width_mm(text.english, english_font, size) + gap * scale
    canvas.setFont(japanese_font, size)
    canvas.drawString(japanese_left * mm, baseline * mm, text.japanese)


def _draw_name(canvas: Canvas, card: GeneratedCard, frame: _Frame, top: float) -> float:
    """Draw the name on one centred line, or two when it needs them."""
    style = frame.style
    font = font_for(card.name, bold=True)
    lines = wrap(
        card.name,
        frame.inner_width,
        font=font,
        size_pt=style.title_size_pt,
        max_lines=MAX_NAME_LINES,
    )
    canvas.setFillColorRGB(*INK)
    canvas.setFont(font, style.title_size_pt)
    baseline = top - style.name_line_mm
    for line in lines:
        canvas.drawCentredString(frame.centre * mm, baseline * mm, line)
        baseline -= style.name_line_mm
    return top - max(len(lines), 1) * style.name_line_mm - style.block_gap_mm


def _draw_stats(canvas: Canvas, card: GeneratedCard, frame: _Frame, top: float) -> float:
    """Draw the three battle numbers as tiles, each named in both languages."""
    style = frame.style
    character = card.character
    tiles = (
        ("HP", character.hp, draw_heart),
        ("ST", character.st, draw_sword),
        ("DF", character.df, draw_shield),
    )
    gap = 1.6
    tile_width = (frame.inner_width - gap * (len(tiles) - 1)) / len(tiles)
    tile_height = style.stat_block_mm
    bottom = top - tile_height
    for index, (key, value, icon) in enumerate(tiles):
        left = frame.inner_left + index * (tile_width + gap)
        centre = left + tile_width / 2
        colours = STAT_STYLES[key]
        canvas.saveState()
        canvas.setFillColorRGB(*colours.tint)
        canvas.setStrokeColorRGB(*colours.icon)
        canvas.setLineWidth(0.4)
        canvas.roundRect(
            left * mm, bottom * mm, tile_width * mm, tile_height * mm, 1.6 * mm, stroke=1, fill=1
        )
        canvas.restoreState()
        icon(
            canvas,
            x_mm=centre - style.stat_icon_mm / 2,
            y_mm=bottom + tile_height - style.stat_icon_mm - 1.1,
            size_mm=style.stat_icon_mm,
        )
        number = str(value)
        number_font = font_for(number, bold=True)
        canvas.setFillColorRGB(*INK)
        canvas.setFont(
            number_font, fit_size(number, number_font, tile_width - 1.6, style.stat_size_pt)
        )
        canvas.drawCentredString(centre * mm, (bottom + 4.2) * mm, number)
        canvas.setFillColorRGB(*MUTED_INK)
        _draw_pair(
            canvas,
            STAT_LABELS[key],
            x=centre,
            baseline=bottom + 1.2,
            size_pt=style.stat_label_size_pt,
            available=tile_width - 1.2,
            bold=True,
            centred=True,
            gap=PAIR_GAP_MM / 2,
        )
    return bottom - style.block_gap_mm


def _draw_ability(
    canvas: Canvas, card: GeneratedCard, frame: _Frame, *, top: float, bottom: float
) -> None:
    """Draw the special power: a pictogram, then its effect in both languages."""
    style = frame.style
    special = card.character.special
    height = top - bottom
    canvas.saveState()
    canvas.setFillColorRGB(*PANEL_FILL)
    canvas.roundRect(
        frame.inner_left * mm,
        bottom * mm,
        frame.inner_width * mm,
        height * mm,
        1.6 * mm,
        stroke=0,
        fill=1,
    )
    canvas.restoreState()

    icon_size = min(style.ability_icon_mm, height - 2.0)
    draw_ability_icon(
        canvas,
        special,
        x_mm=frame.inner_left + 1.2,
        y_mm=top - 1.0 - icon_size,
        size_mm=icon_size,
    )
    text_left = frame.inner_left + 1.2 + icon_size + 1.6
    available = frame.x + frame.width - style.padding_mm - 1.2 - text_left
    header = Bilingual(f"{SPECIAL_POWER.english} {special.code:02d}", SPECIAL_POWER.japanese)
    canvas.setFillColorRGB(*MUTED_INK)
    _draw_pair(
        canvas,
        header,
        x=text_left,
        baseline=top - 2.6,
        size_pt=style.ability_label_size_pt,
        available=available,
        bold=True,
    )
    lines = _ability_lines(ability_text(special), available, height, style)
    canvas.setFillColorRGB(*INK)
    baseline = top - 2.6 - style.ability_line_mm
    for line, font in lines:
        canvas.setFont(font, style.ability_size_pt)
        canvas.drawString(text_left * mm, baseline * mm, line)
        baseline -= style.ability_line_mm


def _ability_lines(
    text: Bilingual, available: float, height: float, style: CardStyle
) -> list[tuple[str, str]]:
    """Share the panel's lines between the two languages, English first.

    Japanese always keeps at least one line. Whatever English does not use goes
    to Japanese.
    """
    budget = max(2, int((height - 3.4) / style.ability_line_mm))
    english_font = font_for(text.english)
    japanese_font = font_for(text.japanese)
    english = wrap(
        text.english,
        available,
        font=english_font,
        size_pt=style.ability_size_pt,
        max_lines=budget - 1,
    )
    japanese = wrap(
        text.japanese,
        available,
        font=japanese_font,
        size_pt=style.ability_size_pt,
        max_lines=budget - len(english),
    )
    return [(line, english_font) for line in english] + [(line, japanese_font) for line in japanese]


def _draw_barcode(
    canvas: Canvas,
    card: GeneratedCard,
    frame: _Frame,
    symbol_width: float,
    geometry: BarcodeGeometry,
) -> float:
    """Draw the symbol at the foot, captioned in both languages, and return its top.

    The digits under the bars are drawn by the symbol itself, in the zone the
    standard reserves for them. Printing them a second time would put an
    unrelated line of text inside the quiet zone below the bars.
    """
    style = frame.style
    symbol_x = frame.x + (frame.width - symbol_width) / 2
    _, symbol_height = draw_symbol(
        canvas, card.barcode, x_mm=symbol_x, y_mm=frame.y + style.padding_mm, geometry=geometry
    )
    caption_baseline = frame.y + style.padding_mm + symbol_height + 1.0
    canvas.setFillColorRGB(*MUTED_INK)
    _draw_pair(
        canvas,
        SWIPE,
        x=frame.centre,
        baseline=caption_baseline,
        size_pt=style.swipe_size_pt,
        available=frame.inner_width,
        centred=True,
        gap=SWIPE_GAP_MM,
    )
    return caption_baseline + style.swipe_block_mm - 1.0
