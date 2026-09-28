"""The barcodes Lupin Sansei: Densetsu no Hihou o Oe! reads on its password screen.

Epoch's Super Famicom game of 1994 reads a code only while its title menu's
password screen is open ($C0:13DF). The reception routine at $C0:220B stores
the digits last first ($C0:22FC), and $C0:237F compares them with the eleven
rows at $C0:23F7, where $FE matches any digit. The first matching row is the
effect, and a code that matches none only plays the error sound. The check
digit is never tested. Confirmed against the game in MAME on 250 codes.
"""

from typing import Final

from maeyomi.games.effects import Effect, EffectGame
from maeyomi.models.device import Device

ANY: Final = "*"
ROWS: Final = (
    "**5**0*******",
    "*02**********",
    "*22**********",
    "*42**********",
    "*62**********",
    "**00*********",
    "**02*********",
    "**04*********",
    "**06*********",
    "**3**********",
    "8*1**********",
)
"""$C0:23F7: each row against the digits last first, the check digit leading."""

EFFECTS: Final = (
    Effect(
        0,
        ("No damage", "ノーダメージ"),
        ("Lupin loses no life to any hit", "ルパンが ダメージを うけない"),
        "4903175035500",
    ),
    Effect(
        1, ("Story A", "ストーリー A"), ("Starts story route A", "ルート A から"), "4997966015208"
    ),
    Effect(
        2, ("Story B", "ストーリー B"), ("Starts story route B", "ルート B から"), "4944330386228"
    ),
    Effect(
        3, ("Story C", "ストーリー C"), ("Starts story route C", "ルート C から"), "4918594007243"
    ),
    Effect(
        4, ("Story D", "ストーリー D"), ("Starts story route D", "ルート D から"), "4946674236269"
    ),
    Effect(
        5,
        ("Ending A", "エンディング A"),
        ("Plays ending A", "エンディング A を みる"),
        "4971845380007",
    ),
    Effect(
        6,
        ("Ending B", "エンディング B"),
        ("Plays ending B", "エンディング B を みる"),
        "4968208432039",
    ),
    Effect(
        7,
        ("Ending C", "エンディング C"),
        ("Plays ending C", "エンディング C を みる"),
        "4997164854081",
    ),
    Effect(
        8,
        ("Ending D", "エンディング D"),
        ("Plays ending D", "エンディング D を みる"),
        "4928498496005",
    ),
    Effect(
        9,
        ("Sound test", "サウンドテスト"),
        ("Opens the sound test", "サウンドテストを ひらく"),
        "4926611518399",
    ),
    Effect(
        10,
        ("Item max", "アイテム マックス"),
        ("Fills all four items to 9", "4つの アイテムを 9こに"),
        "4905638931138",
    ),
)


def lupin_rule(digits: str) -> int | None:
    """The first row the digits, read last first, match, or None."""
    reversed_digits = digits[::-1]
    return next(
        (
            index
            for index, row in enumerate(ROWS)
            if all(want in {ANY, have} for want, have in zip(row, reversed_digits, strict=True))
        ),
        None,
    )


LUPIN: Final = EffectGame(
    device=Device.LUPIN,
    rule=lupin_rule,
    effects=EFFECTS,
    strongest=0,
    screen=(
        "Scan it on the title menu's password screen",
        "タイトルの パスワード がめんで よませる",
    ),
)
