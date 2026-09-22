"""Typed rejections raised when a barcode cannot be read.

The device accepts only 8 and 13 digit codes with a valid EAN check digit, per
`check_barcode` and `check_degit` in `src/BarcodeRead.as` of
finalfighter/BarcodeBattler2-Simulator (MIT). Every rejection names the rule it
failed so a caller can tell the user what to change.
"""

from barcode_battler.decoder.check_digit import EAN_8_LENGTH, EAN_13_LENGTH


class BarcodeError(ValueError):
    """Base class for every reason a barcode cannot be decoded."""


class InvalidLengthError(BarcodeError):
    """The code is not 8 or 13 digits long."""

    def __init__(self, length: int) -> None:
        """Record the rejected length."""
        self.length = length
        super().__init__(f"barcode must be {EAN_8_LENGTH} or {EAN_13_LENGTH} digits, got {length}")


class InvalidCharacterError(BarcodeError):
    """The code contains something other than decimal digits."""

    def __init__(self, barcode: str) -> None:
        """Record the rejected barcode."""
        self.barcode = barcode
        super().__init__(f"barcode must contain only digits, got {barcode!r}")


class CheckDigitError(BarcodeError):
    """The final digit does not match the EAN check digit for the rest of the code."""

    def __init__(self, barcode: str, expected: int) -> None:
        """Record the barcode and the digit that would have been correct."""
        self.barcode = barcode
        self.expected = expected
        super().__init__(f"check digit of {barcode!r} is {barcode[-1]}, expected {expected}")


class UnsupportedBarcodeError(BarcodeError):
    """The code is well formed but this decoder declines to read it."""

    def __init__(self, barcode: str, reason: str) -> None:
        """Record the barcode and why this decoder declines it."""
        self.barcode = barcode
        self.reason = reason
        super().__init__(f"cannot decode {barcode!r}: {reason}")
