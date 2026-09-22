"""The EAN check digit the device verifies before it reads any barcode.

Source: `check_degit` in `src/BarcodeRead.as` of
finalfighter/BarcodeBattler2-Simulator (MIT). An 8-digit code is left-padded
with five zeros so that one routine serves both supported lengths, and the
padding is what makes the weight parity of the two cases agree.
"""

from typing import Final

EAN_13_LENGTH: Final = 13
EAN_8_LENGTH: Final = 8
_ODD_POSITION_WEIGHT: Final = 3
_PAD = "0" * (EAN_13_LENGTH - EAN_8_LENGTH)


def expected_check_digit(code: str) -> int:
    """Return the check digit for a code, ignoring any check digit already present.

    Accepts a full 8 or 13 digit code, or a body of 7 or 12 digits.
    """
    body = _body(code)
    even = sum(int(body[index]) for index in range(0, len(body), 2))
    odd = sum(int(body[index]) for index in range(1, len(body), 2))
    return (10 - (even + odd * _ODD_POSITION_WEIGHT) % 10) % 10


def _body(code: str) -> str:
    """Normalise any accepted input to the twelve digits the weighting runs over."""
    if not code.isdigit():
        message = f"barcode must contain only digits, got {code!r}"
        raise ValueError(message)
    trimmed = {
        EAN_13_LENGTH: code[:-1],
        EAN_13_LENGTH - 1: code,
        EAN_8_LENGTH: _PAD + code[:-1],
        EAN_8_LENGTH - 1: _PAD + code,
    }.get(len(code))
    if trimmed is None:
        message = f"barcode must be 8 or 13 digits, got {len(code)} digits"
        raise ValueError(message)
    return trimmed
