"""The item cards J.League Excite Stage '95 reads through the Barcode Battler II.

Epoch's Super Famicom game of 1995 reads a code on its Barcode Battler II
input screen, which opens before an open match, a league, a tournament or a
dream match. $AB:A938 reads the digits in place: the eighth and ninth choose
one of four abilities, the tenth to twelfth make a number N, and the check
digit decides the rest. Below 8, the card raises that ability by N x 65 / 256,
or a keeper's saving when the second and eighth digits add up odd. At 8 or
9, it is a special card: N even gives handicap points, N odd stops fouls from
showing cards, by one to four from the ability digits. PK mode reads codes
another way and is not modelled. Confirmed against the game in MAME.
"""

import itertools
from collections.abc import Iterator
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, required
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.device import Device

OVERALL: Final = 0
DRIBBLE: Final = 1
PASS_SPEED: Final = 2
KICK_SPEED: Final = 3
SAVING: Final = 4
HANDICAP: Final = 5
NO_CARDS: Final = 6
SPECIAL_CHECK: Final = 8
SCALE: Final = 65
SHIFT: Final = 8
TOP_VALUE: Final = 253
SELECTORS: Final = 4
TOP_N: Final = 999
LEAD: Final = "4"
SPECIAL_VALUES: Final = range(1, SELECTORS + 1)
FREE_DIGITS: Final = 3

ITEMS: Final = {
    OVERALL: ("Overall power", "そうりょく"),
    DRIBBLE: ("Dribble", "ドリブル"),
    PASS_SPEED: ("Pass speed", "パススピード"),
    KICK_SPEED: ("Kick speed", "キックスピード"),
    SAVING: ("Keeper saving", "セービング"),
    HANDICAP: ("Handicap points", "ハンデ ポイント"),
    NO_CARDS: ("No cards for fouls", "ファウルで カードが でない"),
}


def decode_excite95(code: str) -> DatachCard:
    """The item a barcode is, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    digits = [int(character) for character in normalised.rjust(13, "0")]
    selector = (10 * digits[7] + digits[8]) % SELECTORS
    number = 100 * digits[9] + 10 * digits[10] + digits[11]
    if digits[12] >= SPECIAL_CHECK:
        kind = NO_CARDS if number % 2 else HANDICAP
        return DatachCard(normalised, Device.EXCITE95, GameKind.ITEM, kind, (), (selector + 1,))
    kind = SAVING if (digits[7] + digits[1]) % 2 else selector
    value = (number * SCALE) >> SHIFT
    return DatachCard(normalised, Device.EXCITE95, GameKind.ITEM, kind, (), (value,))


def build_excite95(kind: int, value: int) -> DatachCard | None:
    """The first code that reads as this item with this value, or None."""
    cards = (decode_excite95(code) for code in _codes(kind, value))
    return next((card for card in cards if (card.ident, card.traits) == (kind, (value,))), None)


def strongest_excite95() -> DatachCard:
    """Overall power raised by the most a card can raise it."""
    return required(
        build_excite95(OVERALL, TOP_VALUE), "the strongest Excite Stage '95 card cannot be printed"
    )


def _codes(kind: int, value: int) -> Iterator[str]:
    """Every code whose digits could make this item with this value."""
    special = kind in {HANDICAP, NO_CARDS}
    if special and value not in SPECIAL_VALUES:
        return
    numbers = [n for n in range(TOP_N + 1) if _fits(n, kind, value, special=special)]
    selectors = [value - 1] if special else ([kind] if kind != SAVING else range(SELECTORS))
    for number, selector, free in itertools.product(
        numbers, selectors, itertools.product(range(10), repeat=FREE_DIGITS)
    ):
        second = 1 if kind == SAVING else 0
        body = f"{LEAD}{second}{''.join(map(str, free))}000{selector}{number:03d}"
        yield body + str(expected_check_digit(body))


def _fits(number: int, kind: int, value: int, *, special: bool) -> bool:
    """Whether N gives this value, or for a special card this kind."""
    if special:
        return number % 2 == (kind == NO_CARDS)
    return (number * SCALE) >> SHIFT == value
