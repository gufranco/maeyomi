"""The 40-bit stream every Datach card game builds from a barcode's digits.

Bandai's Datach games share one routine for this step, relocated per game: ten
of the barcode's digits each give their four bits, lowest first, and a
per-game permutation table scatters those forty bits into five bytes. Each
table entry names a byte in its high nibble and a bit in its low nibble. The
games then read the five bytes from the top bit of the first one.

Ultraman Club, SD Gundam Wars, Yu Yu Hakusho and J.League Super Top Players
send the fourth bit of every digit to one shared bit, so an 8 reads as a 0 and
a 9 as a 1 everywhere except in that bit. Dragon Ball Z keeps all forty.
"""

from typing import Final

from maeyomi.decoder.check_digit import EAN_8_LENGTH, expected_check_digit
from maeyomi.decoder.validation import validate_barcode

STREAM_BYTES: Final = 5
STREAM_BITS: Final = 40
BYTE_BITS: Final = 8
DIGIT_BITS: Final = 4
USED_DIGITS: Final = slice(2, 12)
USED_COUNT: Final = 10
LOW_BITS: Final = 3
EIGHT: Final = 8
LOWEST_WITH_EIGHT: Final = 2

type Permutation = tuple[int, ...]


def stream_position(entry: int) -> int:
    """The bit a table entry names, counted from the stream's lowest bit."""
    return (STREAM_BYTES - 1 - (entry >> 4)) * BYTE_BITS + (entry & 0x0F)


def used_digits(code: str) -> list[int]:
    """The ten digits a game reads, with an EAN-8 code's mirrored tail."""
    digits = [int(character) for character in code]
    if len(digits) == EAN_8_LENGTH:
        digits = digits + digits[6:1:-1]
    return digits[USED_DIGITS]


def stream_of(code: str, permutation: Permutation) -> int:
    """The stream a game builds from a validated code's digits."""
    stream = 0
    for index, digit in enumerate(used_digits(code)):
        for bit in range(DIGIT_BITS):
            if digit >> bit & 1:
                stream |= 1 << stream_position(permutation[index * DIGIT_BITS + bit])
    return stream


def field(stream: int, start: int, width: int) -> int:
    """The number held in `width` bits starting `start` bits below the top of the stream."""
    return stream >> (STREAM_BITS - start - width) & ((1 << width) - 1)


def printable_mask(permutation: Permutation) -> int:
    """Every stream bit some digit's three low bits can set."""
    mask = 0
    for index, entry in enumerate(permutation):
        if index % DIGIT_BITS < LOW_BITS:
            mask |= 1 << stream_position(entry)
    return mask


def eight_bit(permutation: Permutation) -> int:
    """The one stream bit every digit's fourth bit is sent to."""
    return 1 << stream_position(permutation[LOW_BITS])


def code_for(stream: int, permutation: Permutation, prefix: str, eights: int = 1) -> str | None:
    """A 13-digit code that builds the stream, or None when no code can.

    The two leading digits are never read, so `prefix` supplies them. When the
    stream sets the shared fourth bit, the first `eights` digits whose three
    low bits are 0 or 1 become 8 or 9; there must be at least one.
    """
    if stream & ~(printable_mask(permutation) | eight_bit(permutation)):
        return None
    digits = _low_digits(stream, permutation)
    if stream & eight_bit(permutation):
        candidates = [index for index, digit in enumerate(digits) if digit < LOWEST_WITH_EIGHT]
        if not candidates or eights < 1:
            return None
        chosen = frozenset(candidates[:eights])
        digits = [digit + EIGHT if index in chosen else digit for index, digit in enumerate(digits)]
    body = prefix + "".join(str(digit) for digit in digits)
    return validate_barcode(body + str(expected_check_digit(body)))


def _low_digits(stream: int, permutation: Permutation) -> list[int]:
    """Each digit's three low bits, read back out of the stream."""
    return [
        sum(
            1 << bit
            for bit in range(LOW_BITS)
            if stream >> stream_position(permutation[index * DIGIT_BITS + bit]) & 1
        )
        for index in range(USED_COUNT)
    ]
