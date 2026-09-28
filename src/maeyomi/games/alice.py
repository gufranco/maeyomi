"""The barcodes Alice no Paint Adventure reads on its adventure password screen.

Epoch's Super Famicom game of 1995 reads a code only on the password screen
of its adventure story, while its mode byte is 9 ($C0:19F4). $C4:749D
compares the digits with 32 patterns at $C4:7513, where $0F matches any
digit and $0E matches none, and the first match fills the four portraits
with that entry's password from $C4:5D94. Pressing OK then starts the story
where that password does. Entry 31 goes straight to the staff roll.
Confirmed against the game in MAME on 253 codes.
"""

from typing import Final

from maeyomi.games.effects import Effect, EffectGame
from maeyomi.models.device import Device

ANY: Final = "*"
PATTERNS: Final = (
    (0, "********4***9"),
    (1, "********4***8"),
    (2, "********4***7"),
    (5, "********4***5"),
    (6, "********4***4"),
    (9, "********4***2"),
    (10, "********4***1"),
    (14, "********4***0"),
    (17, "********8***8"),
    (18, "********8***7"),
    (22, "4905040098***"),
    (25, "********2***5"),
    (26, "********5***4"),
    (29, "********2***4"),
    (30, "********2***3"),
    (31, "490504012***2"),
)
"""$C4:7513, in the game's order, without the entries no digit can reach."""

LATE_FLAGS: Final = ("with three late-story flags set", "ものがたりの あとの フラグ 3つ つき")
EFFECTS: Final = (
    Effect(
        0,
        ("Chapter 1, scene 1", "1しょう 1ばめん"),
        ("Starts the story at the beginning", "さいしょ から"),
        "4955641445559",
    ),
    Effect(
        1,
        ("Chapter 2, scene 1", "2しょう 1ばめん"),
        ("Starts chapter 2", "2しょう から"),
        "4933477941308",
    ),
    Effect(
        2,
        ("Chapter 2, scene 2", "2しょう 2ばめん"),
        ("Starts chapter 2, scene 2", "2しょう 2ばめん から"),
        "4996552042987",
    ),
    Effect(
        5,
        ("Chapter 3, scene 3", "3しょう 3ばめん"),
        ("Starts chapter 3, scene 3", "3しょう 3ばめん から"),
        "4924350944325",
    ),
    Effect(
        6,
        ("Chapter 3, scene 4", "3しょう 4ばめん"),
        ("Starts chapter 3, scene 4", "3しょう 4ばめん から"),
        "3581363047194",
    ),
    Effect(
        9,
        ("Chapter 4, scene 3", "4しょう 3ばめん"),
        ("Starts chapter 4, scene 3", "4しょう 3ばめん から"),
        "4915269545932",
    ),
    Effect(
        10,
        ("Chapter 4, scene 4", "4しょう 4ばめん"),
        ("Starts chapter 4, scene 4", "4しょう 4ばめん から"),
        "4993287148021",
    ),
    Effect(
        14,
        ("Chapter 4, scene 8", "4しょう 8ばめん"),
        ("Starts chapter 4, scene 8", "4しょう 8ばめん から"),
        "4939766745350",
    ),
    Effect(
        17,
        ("Chapter 5, scene 3", "5しょう 3ばめん"),
        ("Starts chapter 5, scene 3", "5しょう 3ばめん から"),
        "4929796081818",
    ),
    Effect(
        18,
        ("Chapter 5, scene 4", "5しょう 4ばめん"),
        ("Starts chapter 5, scene 4", "5しょう 4ばめん から"),
        "4956980088407",
    ),
    Effect(
        22,
        ("The castle", "おしろ"),
        (
            "Starts chapter 5, scene 8, the castle, from the box's barcode",
            "はこの バーコードで 5しょう 8ばめん、おしろ から",
        ),
        "4905040098351",
    ),
    Effect(
        25,
        ("Chapter 5, scene 3, late", "5しょう 3ばめん、あと"),
        ("Starts chapter 5, scene 3 " + LATE_FLAGS[0], "5しょう 3ばめん から、" + LATE_FLAGS[1]),
        "4976388928815",
    ),
    Effect(
        26,
        ("Chapter 5, scene 4, late", "5しょう 4ばめん、あと"),
        ("Starts chapter 5, scene 4 " + LATE_FLAGS[0], "5しょう 4ばめん から、" + LATE_FLAGS[1]),
        "4996766955974",
    ),
    Effect(
        29,
        ("Chapter 5, scene 7, late", "5しょう 7ばめん、あと"),
        ("Starts chapter 5, scene 7 " + LATE_FLAGS[0], "5しょう 7ばめん から、" + LATE_FLAGS[1]),
        "4934967722414",
    ),
    Effect(
        30,
        ("Chapter 5, scene 8, late", "5しょう 8ばめん、あと"),
        ("Starts chapter 5, scene 8 " + LATE_FLAGS[0], "5しょう 8ばめん から、" + LATE_FLAGS[1]),
        "4983977828913",
    ),
    Effect(
        31,
        ("Staff roll", "スタッフロール"),
        ("Goes straight to the staff roll", "すぐに スタッフロール"),
        "4905040126252",
    ),
)
LAST_SCENE: Final = 30


def alice_rule(digits: str) -> int | None:
    """The entry of the first pattern the digits match, or None."""
    return next(
        (
            entry
            for entry, pattern in PATTERNS
            if all(want in {ANY, have} for want, have in zip(pattern, digits, strict=True))
        ),
        None,
    )


ALICE: Final = EffectGame(
    device=Device.ALICE,
    rule=alice_rule,
    effects=EFFECTS,
    strongest=LAST_SCENE,
    screen=(
        "Scan it on the adventure story's password screen",
        "おはなし の ぼうけんの パスワード がめんで よませる",
    ),
)
