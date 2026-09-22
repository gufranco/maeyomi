"""Colour measurements the card palette is chosen against.

The cards are printed by commercial printers, which often means black and
white, and they are handed to children, some of whom will not see red and green
apart. Both cases are handled by measurement rather than by taste, so this
module carries the arithmetic and the palette is tested against it.

Three questions get answered here:

- Is white text readable on this band, in colour and in grey? That is the WCAG
  contrast ratio, whose 4.5 to 1 threshold for text depends only on relative
  luminance, so a colour that passes it also passes once the page is printed
  in grey.
- Do two colours stay apart in grey? Same measurement, applied between the two
  colours rather than against white.
- Do two colours stay apart for someone with a colour vision deficiency? That
  needs a simulation of the deficiency, then a perceptual difference.

Sources. The luminance and contrast formulas are WCAG 2.2, Understanding
Success Criterion 1.4.3, <https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum>.
The dichromacy matrices are the linear approximation of Brettel, Vienot and
Mollon, "Computerized simulation of color appearance for dichromats", JOSA A
14(10), 1997, as reformulated by Vienot, Brettel and Mollon (1999). The Lab
conversion is CIE 1976 against the D65 white point.
"""

from enum import Enum
from typing import Final

Colour = tuple[float, float, float]
Matrix = tuple[Colour, Colour, Colour]

_SRGB_LINEAR_CUTOFF: Final = 0.04045
_SRGB_LINEAR_SLOPE: Final = 12.92
_SRGB_GAMMA: Final = 2.4
_SRGB_OFFSET: Final = 0.055
_LUMINANCE_WEIGHTS: Final[Colour] = (0.2126, 0.7152, 0.0722)
_CONTRAST_OFFSET: Final = 0.05

_D65: Final[Colour] = (0.95047, 1.0, 1.08883)
_LAB_EPSILON: Final = 216 / 24389
_LAB_KAPPA: Final = 24389 / 27

_XYZ_FROM_LINEAR: Final[Matrix] = (
    (0.4124564, 0.3575761, 0.1804375),
    (0.2126729, 0.7151522, 0.0721750),
    (0.0193339, 0.1191920, 0.9503041),
)


class ColourVision(Enum):
    """A colour vision deficiency to simulate."""

    PROTANOPIA = "protanopia"
    DEUTERANOPIA = "deuteranopia"
    TRITANOPIA = "tritanopia"


_DICHROMACY: Final[dict[ColourVision, Matrix]] = {
    ColourVision.PROTANOPIA: (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    ColourVision.DEUTERANOPIA: (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    ColourVision.TRITANOPIA: (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


def relative_luminance(colour: Colour) -> float:
    """The WCAG relative luminance of an sRGB colour, 0 for black and 1 for white."""
    linear = _to_linear(colour)
    return sum(weight * channel for weight, channel in zip(_LUMINANCE_WEIGHTS, linear, strict=True))


def contrast_ratio(first: Colour, second: Colour) -> float:
    """The WCAG contrast ratio between two colours, from 1 to 21."""
    lighter, darker = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (lighter + _CONTRAST_OFFSET) / (darker + _CONTRAST_OFFSET)


def greyscale(colour: Colour) -> Colour:
    """The colour as a printer without ink would render it, keeping its lightness."""
    grey = _from_linear_channel(relative_luminance(colour))
    return (grey, grey, grey)


def simulate(colour: Colour, vision: ColourVision) -> Colour:
    """How a colour appears to someone with the given deficiency."""
    linear = _to_linear(colour)
    matrix = _DICHROMACY[vision]
    projected = tuple(
        sum(coefficient * channel for coefficient, channel in zip(row, linear, strict=True))
        for row in matrix
    )
    return tuple(_from_linear_channel(min(max(value, 0.0), 1.0)) for value in projected)  # type: ignore[return-value]


def delta_e(first: Colour, second: Colour) -> float:
    """The CIE 1976 difference between two colours. Around 20 reads as clearly apart."""
    left, right = _to_lab(first), _to_lab(second)
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True)) ** 0.5


def _to_linear(colour: Colour) -> Colour:
    """Undo the sRGB transfer function."""
    return tuple(_to_linear_channel(channel) for channel in colour)  # type: ignore[return-value]


def _to_linear_channel(channel: float) -> float:
    """Undo the sRGB transfer function for one channel."""
    if channel <= _SRGB_LINEAR_CUTOFF:
        return channel / _SRGB_LINEAR_SLOPE
    return ((channel + _SRGB_OFFSET) / (1 + _SRGB_OFFSET)) ** _SRGB_GAMMA


def _from_linear_channel(value: float) -> float:
    """Apply the sRGB transfer function to one channel."""
    if value <= _SRGB_LINEAR_CUTOFF / _SRGB_LINEAR_SLOPE:
        return value * _SRGB_LINEAR_SLOPE
    return (1 + _SRGB_OFFSET) * value ** (1 / _SRGB_GAMMA) - _SRGB_OFFSET


def _to_lab(colour: Colour) -> Colour:
    """Convert an sRGB colour to CIE Lab against the D65 white point."""
    linear = _to_linear(colour)
    xyz = tuple(
        sum(coefficient * channel for coefficient, channel in zip(row, linear, strict=True))
        for row in _XYZ_FROM_LINEAR
    )
    x, y, z = (_lab_f(value / reference) for value, reference in zip(xyz, _D65, strict=True))
    return (116 * y - 16, 500 * (x - y), 200 * (y - z))


def _lab_f(ratio: float) -> float:
    """The cube-root companding CIE Lab applies to each normalised component."""
    if ratio > _LAB_EPSILON:
        return ratio ** (1 / 3)
    return (_LAB_KAPPA * ratio + 16) / 116
