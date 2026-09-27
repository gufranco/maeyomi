"""Whether Datach Dragon Ball Z's reader can read a barcode at all.

The game does not decode digits from a table. It samples the reader, measures
every black bar and every white space, and sorts each set of widths into
classes, one class per distinct width, in the routine at $B085 of its program.
It then accepts the scan only when the class count is 4, or 3, which it maps to
widths 1, 2 and 3 unless its distance check at $B2CD says otherwise ($B2A8).

That rule has two consequences, measured in MAME against the game itself:

- A code whose bars, or whose spaces, come in only two widths can never make
  three classes, so the game refuses it at every swipe speed. 20158231,
  5532403373177 and 6312422195214 failed at every speed from 250 to 1000
  microseconds a module.
- A code whose three widths are 1, 2 and 4 depends on that distance check,
  which depends on how fast the card is swiped: 3623401959035 read at 450, 520
  and 700 microseconds a module and failed at 300, 559, 600 and 900.

Every one of the 232 codes the game accepted has at least three widths in both
its bars and its spaces.
"""

import re
from enum import StrEnum
from typing import Final

from maeyomi.decoder.check_digit import EAN_8_LENGTH
from maeyomi.decoder.errors import BarcodeError

_L: Final = ("0001101", "0011001", "0010011", "0111101", "0100011",
             "0110001", "0101111", "0111011", "0110111", "0001011")  # fmt: skip
_PARITY: Final = ("LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
                  "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL")  # fmt: skip
GUARD: Final = "101"
CENTRE: Final = "01010"
MINIMUM_CLASSES: Final = 3
SPEED_DEPENDENT_WIDTHS: Final = frozenset({1, 2, 4})


class Readability(StrEnum):
    """What the game does with a code that passes its check digit."""

    READS = "reads"
    SPEED_DEPENDENT = "speed dependent"
    REFUSED = "refused"


class ReaderRefusalError(BarcodeError):
    """The code is valid, but the game's reader can never read it."""

    def __init__(self, barcode: str, part: str) -> None:
        """Record the barcode and whether its bars or its spaces are at fault."""
        self.barcode = barcode
        super().__init__(
            f"Datach Dragon Ball Z's reader cannot read {barcode}: its {part} come in only "
            "2 widths, and the game needs 3"
        )


def modules(code: str) -> str:
    """The code as the black (1) and white (0) modules printed on a card."""
    digits = [int(character) for character in code]
    if len(digits) == EAN_8_LENGTH:
        left = "".join(_L[digit] for digit in digits[:4])
        right = digits[4:]
    else:
        parity = _PARITY[digits[0]]
        left = "".join(
            _L[digit] if side == "L" else _mirror(_L[digit])
            for side, digit in zip(parity, digits[1:7], strict=True)
        )
        right = digits[7:]
    return GUARD + left + CENTRE + "".join(_invert(_L[digit]) for digit in right) + GUARD


def width_classes(code: str) -> tuple[frozenset[int], frozenset[int]]:
    """The distinct widths of the code's bars, then of its spaces, in modules."""
    pattern = modules(code)
    bars = frozenset(len(run) for run in re.findall("1+", pattern))
    spaces = frozenset(len(run) for run in re.findall("0+", pattern))
    return bars, spaces


def readability(code: str) -> Readability:
    """Whether the game reads the code always, only at some swipe speeds, or never."""
    bars, spaces = width_classes(code)
    if min(len(bars), len(spaces)) < MINIMUM_CLASSES:
        return Readability.REFUSED
    if SPEED_DEPENDENT_WIDTHS in {bars, spaces}:
        return Readability.SPEED_DEPENDENT
    return Readability.READS


def check_readable(code: str) -> None:
    """Raise when the game's reader can never read the code."""
    bars, spaces = width_classes(code)
    if len(bars) < MINIMUM_CLASSES:
        raise ReaderRefusalError(code, "bars")
    if len(spaces) < MINIMUM_CLASSES:
        raise ReaderRefusalError(code, "spaces")


def _invert(code: str) -> str:
    """An L pattern with black and white swapped, which is the R pattern."""
    return code.translate(str.maketrans("01", "10"))


def _mirror(code: str) -> str:
    """The G pattern: the R pattern read backwards."""
    return _invert(code)[::-1]
