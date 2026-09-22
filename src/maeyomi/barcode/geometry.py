"""Printed geometry for an EAN symbol.

The device reads a swiped card, so the printed size decides whether it reads at
all. Sizes follow the GS1 EAN-13 specification at SC2, the nominal
magnification the retail standard is defined at:

| Quantity | Nominal |
|---|---|
| X-dimension, the module width | 0.330 mm |
| Bar height, the data bars | 22.85 mm |
| Total symbol height, bars plus the digits below them | 25.93 mm |
| Total symbol width, quiet zones included | 37.29 mm |
| Magnification range | 80 to 200 percent, so X from 0.264 to 0.660 mm |

An EAN-13 symbol is 95 modules wide with quiet zones of 11 modules on the left
and 7 on the right; an EAN-8 symbol is 67 modules wide with 7 modules on each
side.

**Height is the number that matters most here, and it is the one most often got
wrong.** A point-of-sale scanner sweeps a laser across the symbol many times a
second. The Barcode Battler has a slot, and a person pushes the card through it
by hand, so the bar height is the whole of the vertical tolerance that person
has. GS1 discourages truncating the bars below the 80 percent height for
scanners that are far more forgiving than a hand swipe. This module therefore
treats the published height as a floor rather than a suggestion.

Nothing here scales an image. The module width is set and the drawing follows
from it, because a rendered symbol scaled to fit a layout rounds its modules
unevenly and stops scanning.
"""

from dataclasses import dataclass
from typing import Final

NOMINAL_MODULE_WIDTH_MM: Final = 0.330
MIN_MODULE_WIDTH_MM: Final = NOMINAL_MODULE_WIDTH_MM * 0.8
MAX_MODULE_WIDTH_MM: Final = NOMINAL_MODULE_WIDTH_MM * 2.0

NOMINAL_BAR_HEIGHT_MM: Final = 22.85
NOMINAL_TOTAL_HEIGHT_MM: Final = 25.93
MIN_BAR_HEIGHT_MM: Final = NOMINAL_BAR_HEIGHT_MM * 0.8
PRINT_DPI: Final = 600

EAN_13_LENGTH: Final = 13
EAN_8_LENGTH: Final = 8

_SYMBOL_MODULES: Final = {EAN_13_LENGTH: 95, EAN_8_LENGTH: 67}
_LEFT_QUIET_MODULES: Final = {EAN_13_LENGTH: 11, EAN_8_LENGTH: 7}
_RIGHT_QUIET_MODULES: Final = {EAN_13_LENGTH: 7, EAN_8_LENGTH: 7}

TEXT_ZONE_MM: Final = 3.38
"""Height the renderer reserves below the data bars for the printed digits.

Measured off a rendered page rather than derived from the published total,
because the two disagree: GS1's 25.93 mm total implies 3.08 mm, while the
widget in use reserves 3.38 mm. Deriving it produced data bars of 22.56 mm
against a 22.85 mm requirement. The bar height is the binding number, so the
measured zone is added to it and the symbol comes out fractionally taller than
the published total, which costs nothing.
"""


@dataclass(frozen=True, slots=True)
class BarcodeGeometry:
    """How large a symbol is printed, in millimetres.

    `bar_height_mm` is the height of the data bars, which is what the
    specification calls the bar height. The guard bars and the space for the
    digits are added on top of it, so the drawn symbol is taller than this
    number by the text zone.
    """

    module_width_mm: float = NOMINAL_MODULE_WIDTH_MM
    bar_height_mm: float = NOMINAL_BAR_HEIGHT_MM
    show_digits: bool = True

    def __post_init__(self) -> None:
        """Reject a size outside what the specification permits."""
        if not MIN_MODULE_WIDTH_MM <= self.module_width_mm <= MAX_MODULE_WIDTH_MM:
            message = (
                f"module width of {self.module_width_mm} mm is outside the permitted "
                f"{MIN_MODULE_WIDTH_MM:.3f} to {MAX_MODULE_WIDTH_MM:.3f} mm"
            )
            raise ValueError(message)
        if self.bar_height_mm < MIN_BAR_HEIGHT_MM:
            message = (
                f"bar height of {self.bar_height_mm} mm truncates the symbol below the "
                f"{MIN_BAR_HEIGHT_MM:.2f} mm floor, which is 80 percent of the "
                f"{NOMINAL_BAR_HEIGHT_MM} mm nominal height"
            )
            raise ValueError(message)

    @property
    def drawn_height_mm(self) -> float:
        """Height the whole symbol occupies, including the digits beneath it."""
        return self.bar_height_mm + TEXT_ZONE_MM

    def symbol_width_mm(self, length: int) -> float:
        """Width of the bars alone, excluding the quiet zones."""
        return _modules(_SYMBOL_MODULES, length) * self.module_width_mm

    def left_quiet_zone_mm(self, length: int) -> float:
        """Required clear space before the first bar."""
        return _modules(_LEFT_QUIET_MODULES, length) * self.module_width_mm

    def right_quiet_zone_mm(self, length: int) -> float:
        """Required clear space after the last bar."""
        return _modules(_RIGHT_QUIET_MODULES, length) * self.module_width_mm

    def total_width_mm(self, length: int) -> float:
        """Width the symbol needs on the page, quiet zones included."""
        return (
            self.left_quiet_zone_mm(length)
            + self.symbol_width_mm(length)
            + self.right_quiet_zone_mm(length)
        )


def _modules(table: dict[int, int], length: int) -> int:
    """Look up a module count, rejecting a length the standard does not define."""
    try:
        return table[length]
    except KeyError:
        message = f"barcode must be {EAN_8_LENGTH} or {EAN_13_LENGTH} digits, got {length}"
        raise ValueError(message) from None
