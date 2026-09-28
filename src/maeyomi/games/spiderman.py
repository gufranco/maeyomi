"""The barcodes The Amazing Spider-Man: Lethal Foes reads on its password screen.

Epoch's Super Famicom game of 1995 reads a code on its 8-letter password
screen through $CA:F8F6, which tests the check digit against one other digit
and writes the result to $0E86. The five results are the password cheats of
$C0:ED00 by another route. Confirmed against the game in MAME on 221 codes.
"""

from typing import Final

from maeyomi.games.effects import Effect, EffectGame
from maeyomi.models.device import Device

DEFEAT: Final = 1
TESTS: Final = (
    ("1", 7, "3", DEFEAT),
    ("0", 9, "6", 2),
    ("7", 4, "0", 4),
    ("5", 10, "4", 3),
    ("4", 10, "5", 5),
)
"""$CA:F8F6: the check digit, a place, the digit it needs there, and $0E86."""

EFFECTS: Final = (
    Effect(
        DEFEAT,
        ("Endless lives", "むげんの ライフ"),
        ("Ten lives that never run down", "へらない 10の ライフ"),
        "4954323394871",
    ),
    Effect(
        2,
        ("HP up", "HP アップ"),
        ("Doubles Spider-Man's health", "たいりょくが 2ばいに"),
        "4903828536170",
    ),
    Effect(
        3,
        ("Nine lives", "ライフ 9"),
        ("Starts with nine lives", "ライフ 9 で スタート"),
        "4928117871435",
    ),
    Effect(
        4,
        ("Boss HP half", "ボス HP はんぶん"),
        ("Halves every boss's health", "ボスの たいりょくが はんぶんに"),
        "4970060136437",
    ),
    Effect(
        5,
        ("Sound test", "サウンドテスト"),
        ("Opens the sound test", "サウンドテストを ひらく"),
        "4915038928584",
    ),
)


def spiderman_rule(digits: str) -> int | None:
    """The first test the check digit and its partner digit pass, or None."""
    check = digits[-1]
    return next(
        (
            result
            for wanted, place, needed, result in TESTS
            if check == wanted and digits[place] == needed
        ),
        None,
    )


SPIDERMAN: Final = EffectGame(
    device=Device.SPIDERMAN,
    rule=spiderman_rule,
    effects=EFFECTS,
    strongest=DEFEAT,
    screen=("Scan it on the title password screen", "タイトルの パスワード がめんで よませる"),
)
