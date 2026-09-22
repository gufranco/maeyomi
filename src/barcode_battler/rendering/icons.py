"""Pictograms drawn on a card face.

These stand in for emoji, and they cannot be emoji. ReportLab's fourteen
built-in fonts carry none, and an embedded emoji font draws flat black outlines
because the colour tables that format uses are not rendered into a PDF. Drawing
the shapes as vectors keeps the colour, stays sharp at print resolution, adds
no font dependency and no licence, and lets each shape be sized to the space it
has.

Every icon draws inside the square it is handed, so a caller reserves a box and
never has to know what goes in it. A race icon is drawn in white on a coloured
band, so the shapes that need a hole in them, an eye or a robot's mouth, are
given the band colour to paint it with.
"""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from math import cos, pi, sin
from typing import Any, Final, cast

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.models.race import Race

Colour = tuple[float, float, float]


def _hex(value: str) -> Colour:
    """Read a six-digit hex colour as three channels."""
    return tuple(int(value[index : index + 2], 16) / 255 for index in (0, 2, 4))  # type: ignore[return-value]


def _tint(colour: Colour, strength: float) -> Colour:
    """A pale version of a colour, for a panel a dark number sits on."""
    return tuple(channel + (1.0 - channel) * strength for channel in colour)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class StatStyle:
    """The colours one battle number is printed in."""

    icon: Colour
    tint: Colour


WHITE: Final[Colour] = (1.0, 1.0, 1.0)
INK: Final[Colour] = _hex("21242E")

STAT_STYLES: Final[dict[str, StatStyle]] = {
    "HP": StatStyle(icon=_hex("C21A2B"), tint=_tint(_hex("C21A2B"), 0.84)),
    "ST": StatStyle(icon=_hex("4A5261"), tint=_tint(_hex("4A5261"), 0.90)),
    "DF": StatStyle(icon=_hex("1B5FA8"), tint=_tint(_hex("1B5FA8"), 0.95)),
}

HP_COLOUR: Final[Colour] = STAT_STYLES["HP"].icon
ST_COLOUR: Final[Colour] = STAT_STYLES["ST"].icon
DF_COLOUR: Final[Colour] = STAT_STYLES["DF"].icon
HILT_COLOUR: Final[Colour] = _hex("B25A00")
BLADE_COLOUR: Final[Colour] = STAT_STYLES["ST"].icon

RACE_COLOURS: Final[dict[Race, Colour]] = {
    Race.MECHANICAL: _hex("666874"),
    Race.ANIMAL: _hex("874F00"),
    Race.AQUATIC: _hex("0375D9"),
    Race.BIRD: _hex("6A2A88"),
    Race.HUMAN: _hex("11401F"),
    Race.SINGLE_USE_WEAPON: _hex("C0431C"),
    Race.WEAPON: _hex("7E1D10"),
    Race.SINGLE_USE_ARMOUR: _hex("3F7099"),
    Race.ARMOUR: _hex("1E4468"),
    Race.SUPPORT_ITEM: _hex("7A5A00"),
}

RACE_LABELS: Final[dict[Race, str]] = {
    Race.MECHANICAL: "Robot",
    Race.ANIMAL: "Animal",
    Race.AQUATIC: "Sea creature",
    Race.BIRD: "Bird",
    Race.HUMAN: "Human",
    Race.SINGLE_USE_WEAPON: "Weapon, one use",
    Race.WEAPON: "Weapon",
    Race.SINGLE_USE_ARMOUR: "Armour, one use",
    Race.ARMOUR: "Armour",
    Race.SUPPORT_ITEM: "Helper item",
}


Point = tuple[float, float]


class _Path:
    """A typed boundary over ReportLab's untyped path object.

    Everything the drawing code touches goes through here, so the shapes below
    are written in ordinary typed Python and the one untyped call site is
    visible in a single place.
    """

    def __init__(self, canvas: Canvas) -> None:
        self._canvas = cast("Any", canvas)
        self._path = cast("Any", canvas.beginPath())

    def move_to(self, point: Point) -> _Path:
        """Start a new subpath."""
        self._path.moveTo(*point)
        return self

    def line_to(self, point: Point) -> _Path:
        """Draw a straight segment."""
        self._path.lineTo(*point)
        return self

    def curve_to(self, control_a: Point, control_b: Point, end: Point) -> _Path:
        """Draw a cubic bezier segment."""
        self._path.curveTo(*control_a, *control_b, *end)
        return self

    def fill(self) -> None:
        """Close the path and fill it with the canvas's current colour."""
        self._path.close()
        self._canvas.drawPath(self._path, stroke=0, fill=1)


@contextmanager
def _box(
    canvas: Canvas, colour: Colour, x_mm: float, y_mm: float, size_mm: float
) -> Generator[tuple[float, float, float]]:
    """Set a fill colour and hand back the drawing box in points."""
    canvas.saveState()
    canvas.setFillColorRGB(*colour)
    try:
        yield (x_mm * mm, y_mm * mm, size_mm * mm)
    finally:
        canvas.restoreState()


def draw_heart(canvas: Canvas, *, x_mm: float, y_mm: float, size_mm: float) -> None:
    """Draw a heart, which marks hit points."""
    with _box(canvas, HP_COLOUR, x_mm, y_mm, size_mm) as (left, bottom, side):

        def at(fx: float, fy: float) -> Point:
            return (left + side * fx, bottom + side * fy)

        (
            _Path(canvas)
            .move_to(at(0.50, 0.04))
            .curve_to(at(0.08, 0.44), at(0.00, 0.74), at(0.25, 0.92))
            .curve_to(at(0.40, 1.02), at(0.50, 0.88), at(0.50, 0.76))
            .curve_to(at(0.50, 0.88), at(0.60, 1.02), at(0.75, 0.92))
            .curve_to(at(1.00, 0.74), at(0.92, 0.44), at(0.50, 0.04))
            .fill()
        )


def draw_sword(canvas: Canvas, *, x_mm: float, y_mm: float, size_mm: float) -> None:
    """Draw a sword, which marks strength."""
    with _box(canvas, BLADE_COLOUR, x_mm, y_mm, size_mm) as (left, bottom, side):

        def at(fx: float, fy: float) -> Point:
            return (left + side * fx, bottom + side * fy)

        (
            _Path(canvas)
            .move_to(at(0.50, 1.00))
            .line_to(at(0.68, 0.78))
            .line_to(at(0.64, 0.32))
            .line_to(at(0.36, 0.32))
            .line_to(at(0.32, 0.78))
            .fill()
        )
        canvas.setFillColorRGB(*HILT_COLOUR)
        canvas.rect(left + side * 0.04, bottom + side * 0.22, side * 0.92, side * 0.10, 0, 1)
        canvas.rect(left + side * 0.42, bottom, side * 0.16, side * 0.22, 0, 1)


def draw_shield(canvas: Canvas, *, x_mm: float, y_mm: float, size_mm: float) -> None:
    """Draw a shield, which marks defence."""
    with _box(canvas, DF_COLOUR, x_mm, y_mm, size_mm) as (left, bottom, side):

        def at(fx: float, fy: float) -> Point:
            return (left + side * fx, bottom + side * fy)

        (
            _Path(canvas)
            .move_to(at(0.50, 1.00))
            .line_to(at(1.00, 0.80))
            .curve_to(at(1.00, 0.34), at(0.82, 0.10), at(0.50, 0.00))
            .curve_to(at(0.18, 0.10), at(0.00, 0.34), at(0.00, 0.80))
            .fill()
        )
        canvas.setFillColorRGB(*WHITE)
        canvas.rect(left + side * 0.44, bottom + side * 0.26, side * 0.12, side * 0.48, 0, 1)
        canvas.rect(left + side * 0.28, bottom + side * 0.44, side * 0.44, side * 0.12, 0, 1)


def draw_race_icon(canvas: Canvas, race: Race, *, x_mm: float, y_mm: float, size_mm: float) -> None:
    """Draw the pictogram for one race, in white, for use on its coloured band."""
    with _box(canvas, WHITE, x_mm, y_mm, size_mm) as box:
        _RACE_ICONS[race](canvas, box, RACE_COLOURS[race])


Box = tuple[float, float, float]


def _scaler(box: Box) -> Callable[[float, float], Point]:
    """Turn fractions of the icon box into points on the page."""
    left, bottom, side = box

    def at(fx: float, fy: float) -> Point:
        return (left + side * fx, bottom + side * fy)

    return at


def _robot(canvas: Canvas, box: Box, background: Colour) -> None:
    """A square head with an antenna, two eyes and a mouth."""
    left, bottom, side = box
    canvas.rect(left + side * 0.47, bottom + side * 0.82, side * 0.06, side * 0.14, 0, 1)
    canvas.circle(left + side * 0.50, bottom + side * 0.94, side * 0.07, 0, 1)
    canvas.roundRect(
        left + side * 0.10, bottom + side * 0.12, side * 0.80, side * 0.70, side * 0.14, 0, 1
    )
    canvas.setFillColorRGB(*background)
    canvas.circle(left + side * 0.32, bottom + side * 0.58, side * 0.09, 0, 1)
    canvas.circle(left + side * 0.68, bottom + side * 0.58, side * 0.09, 0, 1)
    canvas.roundRect(
        left + side * 0.30, bottom + side * 0.26, side * 0.40, side * 0.10, side * 0.04, 0, 1
    )


def _paw(canvas: Canvas, box: Box, _background: Colour) -> None:
    """A pad with four toes."""
    left, bottom, side = box
    canvas.circle(left + side * 0.50, bottom + side * 0.27, side * 0.27, 0, 1)
    for fraction, height in ((0.14, 0.62), (0.38, 0.80), (0.62, 0.80), (0.86, 0.62)):
        canvas.circle(left + side * fraction, bottom + side * height, side * 0.14, 0, 1)


def _fish(canvas: Canvas, box: Box, background: Colour) -> None:
    """A body with a tail fin and an eye."""
    at = _scaler(box)
    (
        _Path(canvas)
        .move_to(at(1.00, 0.50))
        .curve_to(at(0.74, 0.94), at(0.32, 0.94), at(0.18, 0.50))
        .curve_to(at(0.32, 0.06), at(0.74, 0.06), at(1.00, 0.50))
        .fill()
    )
    (_Path(canvas).move_to(at(0.22, 0.50)).line_to(at(0.00, 0.84)).line_to(at(0.00, 0.16)).fill())
    canvas.setFillColorRGB(*background)
    eye = at(0.78, 0.60)
    canvas.circle(eye[0], eye[1], box[2] * 0.07, 0, 1)


def _bird(canvas: Canvas, box: Box, background: Colour) -> None:
    """A head with a beak over a rounded body."""
    at = _scaler(box)
    (
        _Path(canvas)
        .move_to(at(0.72, 0.58))
        .curve_to(at(0.78, 0.14), at(0.28, 0.00), at(0.06, 0.30))
        .curve_to(at(0.16, 0.60), at(0.44, 0.70), at(0.72, 0.58))
        .fill()
    )
    head = at(0.64, 0.74)
    canvas.circle(head[0], head[1], box[2] * 0.20, 0, 1)
    (_Path(canvas).move_to(at(0.82, 0.80)).line_to(at(1.00, 0.70)).line_to(at(0.82, 0.62)).fill())
    canvas.setFillColorRGB(*background)
    eye = at(0.62, 0.80)
    canvas.circle(eye[0], eye[1], box[2] * 0.05, 0, 1)


def _human(canvas: Canvas, box: Box, _background: Colour) -> None:
    """A head over shoulders."""
    at = _scaler(box)
    head = at(0.50, 0.78)
    canvas.circle(head[0], head[1], box[2] * 0.22, 0, 1)
    (
        _Path(canvas)
        .move_to(at(0.04, 0.00))
        .curve_to(at(0.06, 0.52), at(0.94, 0.52), at(0.96, 0.00))
        .fill()
    )


def _weapon(canvas: Canvas, box: Box, _background: Colour) -> None:
    """A sword, marking a weapon card."""
    left, bottom, side = box
    at = _scaler(box)
    (
        _Path(canvas)
        .move_to(at(0.50, 1.00))
        .line_to(at(0.68, 0.76))
        .line_to(at(0.64, 0.28))
        .line_to(at(0.36, 0.28))
        .line_to(at(0.32, 0.76))
        .fill()
    )
    canvas.rect(left + side * 0.06, bottom + side * 0.18, side * 0.88, side * 0.10, 0, 1)
    canvas.rect(left + side * 0.42, bottom, side * 0.16, side * 0.18, 0, 1)


def _armour(canvas: Canvas, box: Box, _background: Colour) -> None:
    """A shield, marking an armour card."""
    at = _scaler(box)
    (
        _Path(canvas)
        .move_to(at(0.50, 1.00))
        .line_to(at(1.00, 0.78))
        .curve_to(at(1.00, 0.32), at(0.82, 0.10), at(0.50, 0.00))
        .curve_to(at(0.18, 0.10), at(0.00, 0.32), at(0.00, 0.78))
        .fill()
    )


def _star(canvas: Canvas, box: Box, _background: Colour) -> None:
    """A five-pointed star, marking a helper item."""
    left, bottom, side = box
    centre_x, centre_y = left + side * 0.5, bottom + side * 0.5
    path = _Path(canvas)
    for index in range(10):
        radius = side * (0.5 if index % 2 == 0 else 0.21)
        angle = pi / 2 + index * pi / 5
        point = (centre_x + radius * cos(angle), centre_y + radius * sin(angle))
        if index:
            path.line_to(point)
        else:
            path.move_to(point)
    path.fill()


_RACE_ICONS: Final[dict[Race, Callable[[Canvas, Box, Colour], None]]] = {
    Race.MECHANICAL: _robot,
    Race.ANIMAL: _paw,
    Race.AQUATIC: _fish,
    Race.BIRD: _bird,
    Race.HUMAN: _human,
    Race.SINGLE_USE_WEAPON: _weapon,
    Race.WEAPON: _weapon,
    Race.SINGLE_USE_ARMOUR: _armour,
    Race.ARMOUR: _armour,
    Race.SUPPORT_ITEM: _star,
}
