"""Read a barcode the way the Barcode Battler II Double reads it.

Source: "BBIIダブルC0" on barcodebattler.net, by alba. The Double has no reader
of its own and takes a code from a Barcode Battler II. It reads it three ways.
The front read and the 49-read are the II's front and back reads, so they are
delegated to this project's II decoder, apart from the speed of a 49-read,
which the source leaves unknown.

The 7-read applies when the first digit is 7 and the tenth is 8, and is the
Double's own:

- HP is the 2nd, 3rd and 12th digits in hundreds;
- ST is the 4th, 5th and 8th, and DF the 6th, 7th and 11th, each up to 99900;
- the job is the 9th digit, and the special power the 3rd and 12th.

The source says its race is still under investigation and gives no speed. A
later report, post 484 of the 5ch thread
https://mevius.5ch.net/test/read.cgi/toy/1226667612/, gives the race as the
8th digit less 5, checked on the 正伝3 and 正伝4 enemy cards; all 11 7-read
cards of the 正伝3 list fit it. Every one of them has an 8th digit of 5 or
more, so below 5 the race stays unknown.
"""

from typing import Final

from maeyomi.decoder.check_digit import EAN_13_LENGTH
from maeyomi.decoder.decode import decode
from maeyomi.decoder.validation import validate_barcode
from maeyomi.double.abilities import DoubleAbility
from maeyomi.double.card import DoubleCard, DoubleReading
from maeyomi.models.character import DISPLAY_SCALE
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType

SEVEN_LEAD: Final = "7"
SEVEN_MARKER_INDEX: Final = 9
SEVEN_MARKER: Final = "8"
HP_DIGITS: Final = (1, 2, 11)
ST_DIGITS: Final = (3, 4, 7)
DF_DIGITS: Final = (5, 6, 10)
SPECIAL_DIGITS: Final = (2, 11)
JOB_INDEX: Final = 8
RACE_INDEX: Final = 7
RACE_OFFSET: Final = 5


def is_seven_read(code: str) -> bool:
    """Whether the Double reads this 13-digit code with its 7-read."""
    return (
        len(code) == EAN_13_LENGTH
        and code[0] == SEVEN_LEAD
        and code[SEVEN_MARKER_INDEX] == SEVEN_MARKER
    )


def decode_double(code: str) -> DoubleCard:
    """Decode a barcode, raising a typed error when the device would reject it."""
    normalised = validate_barcode(code)
    if is_seven_read(normalised):
        return _seven(normalised)
    return _second(normalised)


def _seven(code: str) -> DoubleCard:
    """The Double's own reading of a code that starts with 7 and has 8 tenth."""
    return DoubleCard(
        barcode=code,
        reading=DoubleReading.SEVEN,
        race=_seven_race(code),
        job=int(code[JOB_INDEX]),
        hp=_hundreds(code, HP_DIGITS),
        st=_hundreds(code, ST_DIGITS),
        df=_hundreds(code, DF_DIGITS),
        special=DoubleAbility.from_code(int("".join(code[i] for i in SPECIAL_DIGITS))),
        speed=None,
    )


def _seven_race(code: str) -> Race | None:
    """The race the 8th digit gives, when it is 5 or more."""
    digit = int(code[RACE_INDEX])
    return Race(digit - RACE_OFFSET) if digit >= RACE_OFFSET else None


def _hundreds(code: str, indices: tuple[int, int, int]) -> int:
    """Three digits read as ten thousands, thousands and hundreds."""
    return int("".join(code[i] for i in indices)) * DISPLAY_SCALE


def _second(code: str) -> DoubleCard:
    """The II's reading, with the Double's power table and its unknown 49-read speed."""
    character = decode(code)
    front = character.read_type is ReadType.FRONT
    return DoubleCard(
        barcode=code,
        reading=DoubleReading.FRONT if front else DoubleReading.FORTY_NINE,
        race=character.race,
        job=character.job,
        hp=character.hp,
        st=character.st,
        df=character.df,
        special=DoubleAbility.from_code(character.special.code),
        speed=character.speed if front else None,
        pp=character.pp,
        mp=character.mp,
    )
