"""The numbers Datach Ultraman Club reads a barcode with, copied from its program.

Every table is read out of the game's program ROM, bank 13, at the address
given beside it, and each was checked by running the game in MAME: 51 codes
built from these tables, one per type, and the 38 cards Bandai printed all
showed the type and the three numbers these tables predict.
"""

from typing import Final

PERMUTATION: Final = (
    0x15, 0x21, 0x24, 0x47, 0x26, 0x07, 0x22, 0x47, 0x05, 0x01,
    0x20, 0x47, 0x16, 0x12, 0x10, 0x47, 0x06, 0x25, 0x17, 0x47,
    0x04, 0x23, 0x11, 0x47, 0x13, 0x27, 0x35, 0x47, 0x32, 0x14,
    0x37, 0x47, 0x00, 0x36, 0x33, 0x47, 0x02, 0x34, 0x03, 0x47,
)  # fmt: skip
"""$B38E: where each digit's four bits land in the 40-bit stream."""

TENS: Final = (80, 90, 70, 60, 50, 40, 20, 0, 10, 30, 40, 50, 60, 70, 90, 70)
"""$B699: the tens of a number in hundreds, picked by four bits."""

ADDENDS: Final = (5, 6, 3, 9, 7, 3, 8, 1, 4, 5, 1, 7, 0, 2, 5, 5)
"""$B6A9: the units of a number in hundreds, picked by the next four bits."""

TYPE_SLOTS: Final = (
    (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 1), (9, 1),
    (10, 1), (11, 2), (12, 1), (13, 1), (14, 1), (15, 2), (16, 1), (17, 1), (18, 1), (19, 1),
    (20, 1), (21, 1), (22, 1), (23, 1), (24, 1), (25, 1), (26, 1), (27, 1), (32, 1), (33, 1),
    (34, 1), (35, 1), (36, 1), (37, 1), (38, 1), (39, 1), (40, 1), (41, 1), (42, 1), (43, 1),
    (44, 1), (45, 1), (46, 1), (47, 1), (48, 2), (49, 2), (50, 1), (51, 1), (52, 1), (53, 2),
    (54, 1),
)  # fmt: skip
"""$B6B9: each type and how many of the 64 six-bit values name it, in order."""

FIRST_ITEM: Final = 32
"""The game treats every type from 32 up as an item: it compares against $20 throughout."""
