"""The players and items J.League Excite Stage '94 reads through the Barcode Battler II.

Epoch's Super Famicom game of 1994 reads a code on the Barcode Battler panel
of its roster screen before a pre-season match ($A7:F252). A check digit of 4
or more is one of 240 hidden players: an eighth digit of 6 or more makes a
keeper from the ninth to twelfth digits, anything lower a field player from
the eighth to twelfth, and the sum picks the team and the slot ($A7:F30C).
A lower check digit is an item card that raises one ability by N x 65 / 256,
where N is the tenth to twelfth digits: a keeper's saving when the second and
eighth digits add up odd, else the ability the eighth and ninth choose. PK
mode reads a player the same way; an item there takes one of six PK types
from the eighth and ninth digits' sum modulo 6 ($A5:9951) and a level from
half the eleventh and twelfth digits' sum ($A7:F2E3), named on the PK screen as
kick speed, control, curve shots, saving, quickness or instant saves. Confirmed
against the game in MAME on both screens.
"""

import itertools
from collections.abc import Iterator
from functools import cache
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, required
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.device import Device

FIRST_TEAM: Final = 12
SLOTS: Final = 20
PLAYER_CHECK: Final = 4
KEEPER_EIGHTH: Final = 6
KEEPER_SLOTS: Final = (0, 15)
FIELD_SLOTS: Final = 18
SKIPPED_SLOT: Final = 15
OVERALL: Final = 0
DRIBBLE: Final = 1
PASS_SPEED: Final = 2
KICK_SPEED: Final = 3
SAVING: Final = 4
FIRST_ITEM: Final = 1000
SELECTORS: Final = 4
SCALE: Final = 65
SHIFT: Final = 8
TOP_VALUE: Final = 253
TOP_N: Final = 999
BEST: Final = FIRST_TEAM * SLOTS + 12
FIRST_PK_ITEM: Final = 8
PK_ITEMS: Final = 6
ITEMS: Final = {
    OVERALL: ("Overall power", "そうりょく"),
    DRIBBLE: ("Dribble", "ドリブル"),
    PASS_SPEED: ("Pass speed", "パススピード"),
    KICK_SPEED: ("Kick speed", "キックスピード"),
    SAVING: ("Keeper saving", "セービング"),
}


def player_ident(team: int, slot: int) -> int:
    """The key a hidden player is filed under."""
    return team * SLOTS + slot


def decode_excite94(code: str) -> DatachCard:
    """The player or item a barcode is, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    digits = [int(character) for character in normalised.rjust(13, "0")]
    if digits[12] >= PLAYER_CHECK:
        keeper, ident = _player(digits)
        return DatachCard(normalised, Device.EXCITE94, GameKind.PLAYER, ident, (), (keeper,))
    kind = SAVING if (digits[1] + digits[7]) % 2 else (digits[7] + digits[8]) % SELECTORS
    value = ((100 * digits[9] + 10 * digits[10] + digits[11]) * SCALE) >> SHIFT
    return DatachCard(normalised, Device.EXCITE94, GameKind.ITEM, FIRST_ITEM + kind, (), (value,))


PK_ITEM_NAMES: Final = {
    8: ("Kick speed", "キックスピード"),
    9: ("Control", "コントロール"),
    10: ("Curve shots", "カーブシュートの かいすう"),
    11: ("Saving", "セービング"),
    12: ("Quickness", "すばやさ"),
    13: ("Instant saves", "すぐに とめる かいすう"),
}
"""The PK item types, named as the game's PK screen names them."""


def pk_item(code: str) -> tuple[int, int] | None:
    """The PK item type and level a code makes in PK mode, or None when it is a player."""
    return None if decode_excite94(code).kind is GameKind.PLAYER else pk_reading(code)


def pk_reading(code: str) -> tuple[int, int]:
    """The PK item type and level an item code's digits make, per $A7:F2E3."""
    digits = [int(character) for character in validate_barcode(code).rjust(13, "0")]
    return FIRST_PK_ITEM + (digits[7] + digits[8]) % PK_ITEMS, (digits[10] + digits[11]) >> 1


def _player(digits: list[int]) -> tuple[int, int]:
    """Whether the player is a keeper, and which one the digits' sum picks."""
    if digits[7] >= KEEPER_EIGHTH:
        total = (digits[8] >> 1) + (digits[9] & 1) + digits[10] + digits[11] or 1
        return 1, player_ident(FIRST_TEAM + (total >> 1), KEEPER_SLOTS[total & 1])
    total = 100 * (digits[7] & 1) + 10 * digits[8] + digits[9] + digits[10] + (digits[11] & 7)
    team, slot = divmod(total, FIELD_SLOTS)
    slot += 1
    return 0, player_ident(FIRST_TEAM + team, slot + 1 if slot >= SKIPPED_SLOT else slot)


def build_excite94_player(ident: int) -> DatachCard | None:
    """The first code that reads as this hidden player, or None when no code does."""
    code = _first_codes().get(ident)
    return None if code is None else decode_excite94(code)


@cache
def _first_codes() -> dict[int, str]:
    """The first code found for every hidden player a code can reach."""
    found: dict[int, str] = {}
    for code in _player_codes():
        found.setdefault(decode_excite94(code).ident, code)
    return found


def _player_codes() -> Iterator[str]:
    """Codes with every combination of the digits a player is read from."""
    for tail in itertools.product(range(10), repeat=5):
        bodies = (f"49{lead}0000{''.join(map(str, tail))}" for lead in range(10))
        codes = (body + str(expected_check_digit(body)) for body in bodies)
        yield next(code for code in codes if int(code[-1]) >= PLAYER_CHECK)


def build_excite94_item(kind: int, value: int) -> DatachCard | None:
    """The first code that reads as this item with this value, or None."""
    cards = (decode_excite94(code) for code in _item_codes(kind, value))
    wanted = (FIRST_ITEM + kind, (value,))
    return next((card for card in cards if (card.ident, card.traits) == wanted), None)


def _item_codes(kind: int, value: int) -> Iterator[str]:
    """Codes whose digits could make this item with this value."""
    numbers = [n for n in range(TOP_N + 1) if (n * SCALE) >> SHIFT == value]
    selectors = range(SELECTORS) if kind == SAVING else [kind]
    second = 1 if kind == SAVING else 0
    for number, selector, lead in itertools.product(numbers, selectors, range(100)):
        body = f"4{second}{lead:02d}0000{selector}{number:03d}"
        yield body + str(expected_check_digit(body))


def strongest_excite94() -> DatachCard:
    """The hidden player graded A at every ability."""
    return required(
        build_excite94_player(BEST), "the strongest Excite Stage '94 player cannot be printed"
    )
