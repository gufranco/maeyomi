"""Printed geometry for an EAN symbol.

The device reads a swiped card, so the printed size matters as much as the
digits. Sizes follow the EAN specification: a nominal module width of 0.33 mm,
which is the SC2 magnification the retail standard is defined at, with a
permitted range of 80 to 200 percent of it. An EAN-13 symbol is 95 modules wide
with quiet zones of 11 modules on the left and 7 on the right; an EAN-8 symbol
is 67 modules wide with 7 modules on each side.

Nothing here scales an image. The module width is set and the drawing follows
from it, because a rendered symbol scaled to fit a layout rounds its modules
unevenly and stops scanning.
"""

from dataclasses import dataclass
from typing import Final

NOMINAL_MODULE_WIDTH_MM: Final = 0.33
MIN_MODULE_WIDTH_MM: Final = NOMINAL_MODULE_WIDTH_MM * 0.8
MAX_MODULE_WIDTH_MM: Final = NOMINAL_MODULE_WIDTH_MM * 2.0
DEFAULT_HEIGHT_MM: Final = 18.0
PRINT_DPI: Final = 600

EAN_13_LENGTH: Final = 13
EAN_8_LENGTH: Final = 8

_SYMBOL_MODULES: Final = {EAN_13_LENGTH: 95, EAN_8_LENGTH: 67}
_LEFT_QUIET_MODULES: Final = {EAN_13_LENGTH: 11, EAN_8_LENGTH: 7}
_RIGHT_QUIET_MODULES: Final = {EAN_13_LENGTH: 7, EAN_8_LENGTH: 7}


@dataclass(frozen=True, slots=True)
class BarcodeGeometry:
    """How large a symbol is printed, in millimetres."""

    module_width_mm: float = NOMINAL_MODULE_WIDTH_MM
    height_mm: float = DEFAULT_HEIGHT_MM
    show_digits: bool = True

    def __post_init__(self) -> None:
        """Reject a size outside what the EAN specification permits."""
        if not MIN_MODULE_WIDTH_MM <= self.module_width_mm <= MAX_MODULE_WIDTH_MM:
            message = (
                f"module width of {self.module_width_mm} mm is outside the permitted "
                f"{MIN_MODULE_WIDTH_MM:.3f} to {MAX_MODULE_WIDTH_MM:.3f} mm"
            )
            raise ValueError(message)
        if self.height_mm <= 0:
            message = f"height of {self.height_mm} mm must be above zero"
            raise ValueError(message)

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
