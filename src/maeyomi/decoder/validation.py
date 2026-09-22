"""Acceptance rules a barcode must pass before any reading happens.

Source: `check_barcode` and `check_degit` in `src/BarcodeRead.as` of
finalfighter/BarcodeBattler2-Simulator (MIT). A 12-digit UPC-A code is rejected
rather than left-padded, because whether the hardware pads it is an open
question recorded in the project's uncertainty register.
"""

import re
from typing import Final

from maeyomi.decoder.check_digit import (
    EAN_8_LENGTH,
    EAN_13_LENGTH,
    expected_check_digit,
)
from maeyomi.decoder.errors import (
    CheckDigitError,
    InvalidCharacterError,
    InvalidLengthError,
)

SUPPORTED_LENGTHS: Final = (EAN_8_LENGTH, EAN_13_LENGTH)
_SEPARATORS: Final = re.compile(r"[\s\-_]+")


def validate_barcode(code: str) -> str:
    """Return the normalised barcode, raising a typed error when it is unreadable."""
    normalised = _SEPARATORS.sub("", code)
    if not normalised.isdigit():
        raise InvalidCharacterError(barcode=code)
    if len(normalised) not in SUPPORTED_LENGTHS:
        raise InvalidLengthError(length=len(normalised))
    expected = expected_check_digit(normalised)
    if expected != int(normalised[-1]):
        raise CheckDigitError(barcode=normalised, expected=expected)
    return normalised
