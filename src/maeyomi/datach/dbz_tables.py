"""The numbers Datach Dragon Ball Z reads a barcode with.

Read from the game's program, 16 KB bank 14 of the minicart dumped as
`nes_datach` entry `dtc_dbz` in MAME's software list: 262144 bytes, CRC32
19e81461, SHA-1 87478b635fefb25fa13c4876e20f505a97426c1b. Only the numbers are
kept, as the owner decided; how they are used is described in `dbz.py`.

Each constant names the address it was read from, so it can be checked against
a dump.
"""

from typing import Final

PERMUTATION: Final = (
    55, 36, 68, 52, 5, 32, 54, 51, 17, 48, 3, 64, 19, 21, 0, 67, 7, 1, 23, 50,
    20, 35, 69, 34, 39, 16, 38, 70, 2, 65, 49, 53, 18, 33, 4, 66, 6, 71, 22, 37,
)  # fmt: skip
"""$B5CB: where each digit bit lands; high nibble is the byte, low nibble the bit."""

BASES: Final = (
    3000, 2000, 7000, 2000, 5000, 3000, 3000, 3000,
    4000, 4000, 4000, 0, 6000, 1000, 8000, 9000,
)  # fmt: skip
"""$BB4B: the base of a stat, in units of 10, picked by four bits."""

ADDENDS: Final = (
    500, 600, 300, 900, 700, 350, 800, 150,
    400, 500, 100, 750, 0, 200, 550, 500,
)  # fmt: skip
"""$BB6B: what is added to the base, in units of 10, picked by four bits."""

LEVELS: Final = (2, 0, 1, 0, 1, 3, 0, 255)
"""$BB8B: the level picked by three bits; 255 means the character shows none."""

FIGHTER_SLOTS: Final = (
    (0, 5), (8, 4), (6, 4), (3, 4), (4, 4), (5, 4), (2, 5), (7, 4), (1, 4), (22, 3),
    (23, 3), (24, 3), (25, 3), (18, 2), (19, 2), (20, 2), (21, 2), (16, 1), (17, 1),
)  # fmt: skip
"""$BB93: character ids and how many of the 60 slots each takes, in order."""

ITEM_SLOTS: Final = (
    (32, 3), (33, 3), (61, 3), (35, 3), (62, 3), (37, 3), (38, 2), (65, 2), (63, 2),
    (41, 2), (66, 2), (67, 2), (44, 2), (45, 2), (59, 1), (47, 1), (48, 1), (49, 1),
    (52, 1), (51, 1), (50, 1), (53, 1), (54, 1), (55, 1), (56, 1), (57, 1), (58, 1),
    (46, 1), (34, 1), (36, 1), (40, 1), (39, 1), (64, 1), (42, 1), (43, 1), (68, 2),
    (71, 1), (70, 1), (69, 1),
)  # fmt: skip
"""$BBB9: item ids and how many of the 60 slots each takes, in order."""

FORMS: Final = (
    (5500, 3000, 3000, 9),
    (5200, 2700, 2700, 13),
    (5000, 3000, 2000, 10),
    (5500, 3000, 2800, 11),
    (5600, 2900, 2100, 12),
    (4000, 2200, 2000, 27),
    (5000, 2600, 2500, 28),
    (6000, 3000, 3000, 29),
    (3200, 2000, 2000, 26),
    (6000, 3000, 3000, 30),
)
"""$BCE2: minimum HP, BP and DP in units of 10, and the form a character takes."""

FORMS_BY_CHARACTER: Final[dict[int, tuple[int, ...]]] = {
    0: (0,),
    5: (1,),
    6: (2,),
    7: (3,),
    8: (4,),
    16: (5, 6, 7),
    17: (8, 9),
    26: (9,),
    27: (6, 7),
    28: (7,),
}
"""$BC40 and the routines it selects: which form records a character tries, in order."""

SECRET_STREAM: Final = 0xDCB5CB0082
"""$B62C: the one stream the game answers with a fixed card instead of the rule."""

SECRET_CARD: Final = (0, 3, 5900, 4999, 4999)
"""$B600: that card's character, level, and HP, BP and DP in units of 10."""
