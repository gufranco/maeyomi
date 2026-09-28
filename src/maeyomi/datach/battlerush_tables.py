"""The numbers Datach Battle Rush builds a robot from, copied from its program.

Every table is read out of PRG bank 12 at the address given beside it. A
foot is looked up through $97F4 and $8868 before its tables, and feet 30 and
31 run off the end of them into the bytes that follow, which the game reads as
they are. Checked by running the game in MAME on its Robo Factory: every part,
level and pilot the recorded robots used produced the stats these predict.
"""

from typing import Final

SHOULDER_ATTACK: Final = (
    38, 41, 44, 47, 50, 53, 56, 59, 62, 65, 68, 71, 74, 77, 80, 83,
    86, 89, 92, 95, 98, 101, 104, 107, 110, 113, 116, 119, 122, 125, 128, 2,
)  # fmt: skip
"""$986F: the attack each of the 32 shoulders gives."""

HEAD_ATTACK: Final = (
    22, 0, 0, 0, 19, 0, 0, 3, 16, 0, 6, 0, 13, 9, 0, 0,
    11, 0, 5, 6, 7, 7, 8, 0, 4, 6, 6, 6, 5, 5, 6, 0,
)  # fmt: skip
"""$98AD: the attack each head adds."""

BODY_DEFENSE: Final = (
    38, 41, 44, 47, 50, 53, 56, 59, 62, 65, 68, 71, 74, 77, 80, 83,
    86, 89, 92, 95, 98, 101, 104, 107, 110, 113, 116, 119, 122, 125, 128, 25,
)  # fmt: skip
"""$9831: the defense each body gives."""

HEAD_DEFENSE: Final = (
    0, 22, 0, 0, 3, 19, 0, 0, 0, 16, 0, 6, 0, 13, 9, 0,
    6, 11, 0, 5, 0, 7, 7, 8, 6, 4, 6, 6, 5, 6, 6, 0,
)  # fmt: skip
"""$98CC: the defense each head adds."""

HEAD_SPEED: Final = (
    0, 0, 22, 0, 0, 3, 19, 0, 6, 0, 16, 0, 0, 0, 13, 9,
    5, 6, 11, 0, 8, 0, 7, 7, 6, 6, 4, 6, 6, 6, 5, 0,
)  # fmt: skip
"""$98EB: the speed each head adds."""

HEAD_RECOVERY: Final = (
    0, 0, 0, 22, 0, 0, 3, 19, 0, 6, 0, 16, 9, 0, 0, 13,
    0, 5, 6, 11, 7, 8, 0, 7, 6, 6, 6, 4, 6, 5, 5, 34,
)  # fmt: skip
"""$990A: each head's recovery, times 4 plus 62."""

SHOULDER_WEIGHT: Final = (
    25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55,
    57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 38,
)  # fmt: skip
"""$9850: the weight of each shoulder."""

BODY_WEIGHT: Final = (
    25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55,
    57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 38,
)  # fmt: skip
"""$9812: the weight of each body."""

LEVEL_SCALE: Final = (
    100, 110, 120, 130, 140, 150, 160, 170,
)  # fmt: skip
"""$B149: each level's multiplier, in hundredths."""

FOOT_SPEED: Final = (
    101, 98, 95, 92, 89, 86, 83, 80, 77, 74, 71, 68, 65, 62, 59, 56,
    53, 50, 47, 44, 41, 128, 125, 122, 119, 116, 113, 110, 107, 104, 16, 5,
)  # fmt: skip
"""$97D6 through the foot remap: the speed each of the 32 feet gives."""

FOOT_WEIGHT: Final = (
    45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75,
    77, 79, 81, 83, 85, 27, 29, 31, 33, 35, 37, 39, 41, 43, 6, 74,
)  # fmt: skip
"""$97B8 through the foot remap: the weight of each of the 32 feet."""

PILOT_BONUSES: Final[dict[int, tuple[tuple[int, int], ...]]] = {
    0: ((43, 16),),
    1: ((43, 32),),
    2: ((44, 16),),
    3: ((44, 32),),
    4: ((45, 16),),
    5: ((45, 32),),
    6: ((46, 16),),
    7: ((46, 32),),
    8: ((47, 0),),
    9: ((47, 0),),
    10: ((43, 8), (44, 8), (45, 8), (46, 8)),
    11: ((43, 16), (44, 16), (45, 16), (46, 16)),
}
"""$B151: per pilot type, the stat byte, $2B to $2F, and what it adds."""
