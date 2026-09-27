"""Read a barcode the way the first Barcode Battler reads it.

Sources: barcodebattler.co.uk, "Barcode Battler Museum: Original Barcode
Battler", technical info, Method 1 and Method 2; and the note.com analysis of
the original device by sakigomyway. They agree on every rule used here.

A 13-digit code whose leading digit is 0 or 1 is read from the front, with the
same slices as the Barcode Battler II's front read and none of its high health
bonus: health tops out at 19900. Every other code, and every 8-digit code, is
an enemy read from its last five digits. The note.com analysis reads the last
of those, the check digit, as the flag; the UK source found no flag at all.
That disagreement is recorded as `bb1_back_read_flag` and blocks generation.
"""

from typing import Final

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.bb1.flags import Flag
from maeyomi.decoder.check_digit import EAN_13_LENGTH
from maeyomi.decoder.read_type import LOW_LEADING_DIGITS
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.character import DISPLAY_SCALE
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType

HP_SLICE: Final = slice(0, 3)
ST_SLICE: Final = slice(3, 5)
DF_SLICE: Final = slice(5, 7)
RACE_INDEX: Final = 7
JOB_INDEX: Final = 8
DX_INDEX: Final = 9
FLAG_SLICE: Final = slice(10, 12)
ENEMY_JOB: Final = 2
ENEMY_DIGITS: Final = 5
EMPTY_HP_UNITS: Final = 100
BASE_ST_UNITS: Final = 10
EMPTY_DF_UNITS: Final = 1


def decode_first(code: str) -> FirstBattlerCard:
    """Decode a barcode, raising a typed error when the device would reject it."""
    normalised = validate_barcode(code)
    if len(normalised) == EAN_13_LENGTH and int(normalised[0]) in LOW_LEADING_DIGITS:
        return _front(normalised)
    return _back(normalised)


def _front(code: str) -> FirstBattlerCard:
    """A fighter or an item, read from fixed slices."""
    race = Race(int(code[RACE_INDEX]))
    units = {"hp": int(code[HP_SLICE]), "st": int(code[ST_SLICE]), "df": int(code[DF_SLICE])}
    carried = _carried_units(race, units)
    return FirstBattlerCard(
        barcode=code,
        read_type=ReadType.FRONT,
        race=race,
        job=int(code[JOB_INDEX]),
        hp=carried["hp"] * DISPLAY_SCALE,
        st=carried["st"] * DISPLAY_SCALE,
        df=carried["df"] * DISPLAY_SCALE,
        flag=Flag.from_code(int(code[FLAG_SLICE])),
        dx=int(code[DX_INDEX]) if race.is_fighter else None,
    )


def _carried_units(race: Race, units: dict[str, int]) -> dict[str, int]:
    """Keep the numbers this kind of card carries and zero the rest."""
    if race.is_fighter:
        return units
    kept = "st" if race.is_weapon else "df" if race.is_armour else "hp"
    return {name: value if name == kept else 0 for name, value in units.items()}


def _back(code: str) -> FirstBattlerCard:
    """An enemy, read from the last five digits."""
    thousands, hundreds, strength, defence, flag = (int(digit) for digit in code[-ENEMY_DIGITS:])
    hp_units = thousands * 10 + hundreds or EMPTY_HP_UNITS
    return FirstBattlerCard(
        barcode=code,
        read_type=ReadType.BACK,
        race=None,
        job=ENEMY_JOB,
        hp=hp_units * DISPLAY_SCALE,
        st=(BASE_ST_UNITS + strength) * DISPLAY_SCALE,
        df=(defence or EMPTY_DF_UNITS) * DISPLAY_SCALE,
        flag=Flag.from_code(flag),
        dx=None,
    )
