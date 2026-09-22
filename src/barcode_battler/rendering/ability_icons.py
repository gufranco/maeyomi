"""A pictogram for each special power, for a child who cannot read yet.

The picture says what the power touches and which way it moves it: a sword with
an arrow up is stronger attacks, a shield with an arrow down is a weaker defence,
a heart with a question mark is a gamble on health. The direction is carried by
the shape of the arrow and never by its colour.

The icon is a simplification and the words beside it are the rules. It does not
say whose number moves, only which number and in which direction.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Final

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.models.special_ability import UNDOCUMENTED, SpecialAbility
from barcode_battler.rendering.icons import (
    INK,
    WHITE,
    Colour,
    Point,
    VectorPath,
    draw_heart,
    draw_shield,
    draw_sword,
)

BADGE_FONT: Final = "Helvetica-Bold"
GLYPH_SHARE: Final = 0.74
BADGE_SHARE: Final = 0.50
FORBIDDEN_COLOUR: Final[Colour] = (0.72, 0.10, 0.14)


class Glyph(Enum):
    """The main picture: what the power touches."""

    NONE = auto()
    HEART = auto()
    SWORD = auto()
    SHIELD = auto()
    TARGET = auto()
    CROWN = auto()
    KEY = auto()
    CANCEL = auto()
    UNKNOWN = auto()


class Badge(Enum):
    """The small mark in the corner: what happens to it."""

    NONE = auto()
    UP = auto()
    DOWN = auto()
    TRIPLE = auto()
    CHANCE = auto()
    FORBIDDEN = auto()


@dataclass(frozen=True, slots=True)
class AbilityIcon:
    """A glyph and the badge drawn over it."""

    glyph: Glyph
    badge: Badge = Badge.NONE


def _span(first: int, last: int, icon: AbilityIcon) -> dict[int, AbilityIcon]:
    """The same icon for every code in an inclusive range."""
    return dict.fromkeys(range(first, last + 1), icon)


_ICONS: Final[dict[int, AbilityIcon]] = {
    0: AbilityIcon(Glyph.NONE),
    **_span(1, 15, AbilityIcon(Glyph.SWORD, Badge.TRIPLE)),
    16: AbilityIcon(Glyph.SWORD, Badge.DOWN),
    17: AbilityIcon(Glyph.SWORD, Badge.UP),
    18: AbilityIcon(Glyph.SWORD, Badge.UP),
    19: AbilityIcon(Glyph.CROWN),
    **_span(20, 22, AbilityIcon(Glyph.SHIELD, Badge.UP)),
    23: AbilityIcon(Glyph.SWORD, Badge.DOWN),
    24: AbilityIcon(Glyph.SWORD, Badge.DOWN),
    **_span(25, 27, AbilityIcon(Glyph.SHIELD, Badge.DOWN)),
    28: AbilityIcon(Glyph.HEART, Badge.DOWN),
    29: AbilityIcon(Glyph.HEART, Badge.DOWN),
    30: AbilityIcon(Glyph.HEART, Badge.CHANCE),
    31: AbilityIcon(Glyph.SWORD, Badge.CHANCE),
    32: AbilityIcon(Glyph.SHIELD, Badge.CHANCE),
    37: AbilityIcon(Glyph.TARGET, Badge.UP),
    38: AbilityIcon(Glyph.TARGET, Badge.UP),
    39: AbilityIcon(Glyph.TARGET, Badge.UP),
    40: AbilityIcon(Glyph.TARGET, Badge.DOWN),
    41: AbilityIcon(Glyph.TARGET, Badge.DOWN),
    42: AbilityIcon(Glyph.HEART, Badge.FORBIDDEN),
    43: AbilityIcon(Glyph.HEART, Badge.DOWN),
    44: AbilityIcon(Glyph.HEART, Badge.UP),
    45: AbilityIcon(Glyph.CANCEL),
    50: AbilityIcon(Glyph.CROWN),
    **_span(65, 69, AbilityIcon(Glyph.HEART, Badge.UP)),
    **_span(70, 74, AbilityIcon(Glyph.SWORD, Badge.UP)),
    **_span(75, 79, AbilityIcon(Glyph.SHIELD, Badge.UP)),
    **_span(80, 99, AbilityIcon(Glyph.KEY)),
}


def ability_icon(special: SpecialAbility) -> AbilityIcon:
    """The icon for a power, and a question mark for one nobody has documented."""
    if special.description == UNDOCUMENTED:
        return AbilityIcon(Glyph.UNKNOWN)
    return _ICONS[special.code]


def draw_ability_icon(
    canvas: Canvas, special: SpecialAbility, *, x_mm: float, y_mm: float, size_mm: float
) -> None:
    """Draw the icon inside a square whose lower left corner is given."""
    icon = ability_icon(special)
    if icon.glyph is Glyph.NONE:
        return
    glyph_size = size_mm * GLYPH_SHARE
    _GLYPHS[icon.glyph](canvas, x_mm, y_mm + size_mm - glyph_size, glyph_size)
    if icon.badge is not Badge.NONE:
        badge_size = size_mm * BADGE_SHARE
        _draw_badge(canvas, icon.badge, x_mm + size_mm - badge_size, y_mm, badge_size)


def _heart(canvas: Canvas, x: float, y: float, size: float) -> None:
    """A heart: health."""
    draw_heart(canvas, x_mm=x, y_mm=y, size_mm=size)


def _sword(canvas: Canvas, x: float, y: float, size: float) -> None:
    """A sword: attack."""
    draw_sword(canvas, x_mm=x, y_mm=y, size_mm=size)


def _shield(canvas: Canvas, x: float, y: float, size: float) -> None:
    """A shield: defence."""
    draw_shield(canvas, x_mm=x, y_mm=y, size_mm=size)


def _target(canvas: Canvas, x: float, y: float, size: float) -> None:
    """Rings round a bullseye: hitting, and striking first."""
    centre_x, centre_y, radius = (x + size / 2) * mm, (y + size / 2) * mm, size / 2 * mm
    canvas.saveState()
    canvas.setStrokeColorRGB(*INK)
    canvas.setFillColorRGB(*INK)
    canvas.setLineWidth(radius * 0.16)
    canvas.circle(centre_x, centre_y, radius * 0.9, stroke=1, fill=0)
    canvas.circle(centre_x, centre_y, radius * 0.55, stroke=1, fill=0)
    canvas.circle(centre_x, centre_y, radius * 0.2, stroke=0, fill=1)
    canvas.restoreState()


def _crown(canvas: Canvas, x: float, y: float, size: float) -> None:
    """A crown: the hero."""
    left, bottom, side = x * mm, y * mm, size * mm

    def at(fx: float, fy: float) -> Point:
        return (left + side * fx, bottom + side * fy)

    canvas.saveState()
    canvas.setFillColorRGB(*INK)
    (
        VectorPath(canvas)
        .move_to(at(0.04, 0.16))
        .line_to(at(0.04, 0.80))
        .line_to(at(0.30, 0.52))
        .line_to(at(0.50, 0.92))
        .line_to(at(0.70, 0.52))
        .line_to(at(0.96, 0.80))
        .line_to(at(0.96, 0.16))
        .fill()
    )
    canvas.restoreState()


def _key(canvas: Canvas, x: float, y: float, size: float) -> None:
    """A key: a passcode."""
    left, bottom, side = x * mm, y * mm, size * mm
    canvas.saveState()
    canvas.setFillColorRGB(*INK)
    canvas.circle(left + side * 0.28, bottom + side * 0.62, side * 0.24, stroke=0, fill=1)
    canvas.rect(left + side * 0.40, bottom + side * 0.56, side * 0.58, side * 0.12, 0, 1)
    canvas.rect(left + side * 0.80, bottom + side * 0.36, side * 0.10, side * 0.22, 0, 1)
    canvas.rect(left + side * 0.64, bottom + side * 0.40, side * 0.10, side * 0.18, 0, 1)
    canvas.setFillColorRGB(*WHITE)
    canvas.circle(left + side * 0.28, bottom + side * 0.62, side * 0.09, stroke=0, fill=1)
    canvas.restoreState()


def _cancel(canvas: Canvas, x: float, y: float, size: float) -> None:
    """A circle struck through: the opponent's powers switched off."""
    centre_x, centre_y, radius = (x + size / 2) * mm, (y + size / 2) * mm, size / 2 * mm
    canvas.saveState()
    canvas.setStrokeColorRGB(*FORBIDDEN_COLOUR)
    canvas.setLineWidth(radius * 0.22)
    canvas.circle(centre_x, centre_y, radius * 0.86, stroke=1, fill=0)
    offset = radius * 0.6
    canvas.line(centre_x - offset, centre_y + offset, centre_x + offset, centre_y - offset)
    canvas.restoreState()


def _unknown(canvas: Canvas, x: float, y: float, size: float) -> None:
    """A question mark: nobody has written down what this does."""
    _centred_text(canvas, "?", (x + size / 2) * mm, (y + size * 0.14) * mm, size * 0.95)


_GLYPHS: Final[dict[Glyph, Callable[[Canvas, float, float, float], None]]] = {
    Glyph.HEART: _heart,
    Glyph.SWORD: _sword,
    Glyph.SHIELD: _shield,
    Glyph.TARGET: _target,
    Glyph.CROWN: _crown,
    Glyph.KEY: _key,
    Glyph.CANCEL: _cancel,
    Glyph.UNKNOWN: _unknown,
}


def _draw_badge(canvas: Canvas, badge: Badge, x: float, y: float, size: float) -> None:
    """A white disc in the corner carrying the direction or the kind of change."""
    centre_x, centre_y, radius = (x + size / 2) * mm, (y + size / 2) * mm, size / 2 * mm
    canvas.saveState()
    canvas.setFillColorRGB(*WHITE)
    canvas.setStrokeColorRGB(*INK)
    canvas.setLineWidth(radius * 0.12)
    canvas.circle(centre_x, centre_y, radius * 0.94, stroke=1, fill=1)
    canvas.restoreState()
    if badge in {Badge.UP, Badge.DOWN}:
        _arrow(canvas, (centre_x, centre_y), radius, pointing_up=badge is Badge.UP)
    elif badge is Badge.FORBIDDEN:
        _slash(canvas, (centre_x, centre_y), radius)
    else:
        text = "x3" if badge is Badge.TRIPLE else "?"
        _centred_text(canvas, text, centre_x, centre_y - radius * 0.36, size * 0.5)


def _arrow(canvas: Canvas, centre: Point, radius: float, *, pointing_up: bool) -> None:
    """A filled arrow whose direction, not colour, carries the meaning."""
    centre_x, centre_y = centre
    sign = 1 if pointing_up else -1
    tip = centre_y + sign * radius * 0.66
    base = centre_y - sign * radius * 0.05
    stem_end = centre_y - sign * radius * 0.62
    canvas.saveState()
    canvas.setFillColorRGB(*INK)
    (
        VectorPath(canvas)
        .move_to((centre_x, tip))
        .line_to((centre_x + radius * 0.55, base))
        .line_to((centre_x - radius * 0.55, base))
        .fill()
    )
    canvas.rect(
        centre_x - radius * 0.18,
        min(base, stem_end),
        radius * 0.36,
        abs(base - stem_end),
        stroke=0,
        fill=1,
    )
    canvas.restoreState()


def _slash(canvas: Canvas, centre: Point, radius: float) -> None:
    """A stroke through the badge: not allowed."""
    centre_x, centre_y = centre
    canvas.saveState()
    canvas.setStrokeColorRGB(*FORBIDDEN_COLOUR)
    canvas.setLineWidth(radius * 0.28)
    offset = radius * 0.55
    canvas.line(centre_x - offset, centre_y + offset, centre_x + offset, centre_y - offset)
    canvas.restoreState()


def _centred_text(
    canvas: Canvas, text: str, centre_x: float, baseline: float, size_mm: float
) -> None:
    """Bold text centred on a point, sized from a height in millimetres."""
    canvas.saveState()
    canvas.setFillColorRGB(*INK)
    canvas.setFont(BADGE_FONT, size_mm * mm * 1.35)
    canvas.drawCentredString(centre_x, baseline, text)
    canvas.restoreState()
