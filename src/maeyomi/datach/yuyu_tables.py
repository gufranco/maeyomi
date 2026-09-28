"""The numbers Datach Yu Yu Hakusho reads a barcode with, copied from its program.

Every table is read out of the game's program ROM at the address given beside
it, and was checked by running the game in MAME on its analyzer, コエンマの判決,
the second entry of the title menu: 183 codes built from these tables, every
character and item at several technique masks, and the 37 barcodes Bandai
printed all read as these tables predict.
"""

from typing import Final

PERMUTATION: Final = (
    0x15, 0x21, 0x24, 0x47, 0x26, 0x07, 0x22, 0x47, 0x05, 0x06,
    0x20, 0x47, 0x16, 0x12, 0x10, 0x47, 0x01, 0x25, 0x17, 0x47,
    0x00, 0x23, 0x11, 0x47, 0x13, 0x27, 0x35, 0x47, 0x32, 0x14,
    0x37, 0x47, 0x04, 0x36, 0x33, 0x47, 0x02, 0x34, 0x03, 0x47,
)  # fmt: skip
"""Bank 12 $893D: where each digit's four bits land in the 40-bit stream."""

TYPE_SLOTS: Final = (
    (0, 3),
    (1, 3),
    (2, 3),
    (3, 3),
    (4, 2),
    (5, 2),
    (6, 2),
    (7, 2),
    (8, 2),
    (9, 2),
    (10, 2),
    (11, 2),
    (12, 2),
    (13, 2),
    (14, 2),
    (15, 2),
    (16, 2),
    (17, 2),
    (18, 2),
    (19, 2),
    (21, 2),
    (22, 2),
    (32, 2),
    (33, 2),
    (34, 2),
    (35, 2),
    (36, 2),
    (37, 2),
    (38, 1),
    (39, 1),
    (40, 1),
    (41, 1),
)
"""Bank 12 $8C22: each character or item and how many of the 64 six-bit values name it."""

SECRET_STREAM: Final = 0x8B84091880
"""Bank 12 $8980: the one stream the game answers with its hidden character."""

SECRET_CHARACTER: Final = 20
SECRET_MASK: Final = 0x0F

NUMBERS: Final = (
    (3000, 2000),
    (3200, 1800),
    (2500, 2500),
    (2500, 2500),
    (2400, 2600),
    (2400, 2400),
    (2700, 2100),
    (3000, 2200),
    (2400, 2600),
    (2500, 2500),
    (2800, 2300),
    (2900, 2300),
    (2700, 2400),
    (2600, 2500),
    (2800, 2600),
    (2800, 2300),
    (3200, 3000),
    (2700, 2400),
    (4000, 5000),
    (5000, 6500),
    (9999, 9999),
    (2600, 2400),
    (2900, 3000),
)
"""Bank 11 $B752 and $B780: each character's HP and SP, which no barcode changes."""

TECHNIQUES: Final = (
    (64, 65, 67, 66),
    (68, 69, 0, 0),
    (70, 71, 72, 0),
    (74, 73, 75, 0),
    (64, 65, 67, 0),
    (76, 77, 0, 0),
    (78, 79, 0, 0),
    (80, 0, 82, 81),
    (83, 84, 0, 0),
    (86, 85, 0, 0),
    (87, 88, 89, 0),
    (90, 91, 0, 0),
    (92, 93, 0, 0),
    (94, 95, 0, 0),
    (96, 97, 0, 0),
    (98, 99, 0, 0),
    (101, 100, 0, 0),
    (102, 103, 0, 0),
    (48, 49, 82, 50),
    (51, 52, 53, 50),
    (51, 52, 53, 65),
    (64, 65, 54, 0),
    (55, 56, 0, 0),
)
"""$D6E3: each character's four techniques, one per bit of the mask; 0 is none."""

ITEM_BONUSES: Final = (
    ((300, 0), (500, 0), (700, 0), (800, 0)),
    ((400, 0), (600, 0), (800, 0), (1000, 0)),
    ((0, 200), (0, 300), (0, 400), (0, 500)),
    ((0, 250), (0, 350), (0, 450), (0, 550)),
    ((100, 50), (200, 70), (300, 90), (400, 110)),
    ((150, 60), (250, 80), (350, 100), (450, 120)),
    ((65535, 65535), (65535, 65535), (65535, 65535), (65535, 65535)),
    ((65535, 65535), (65535, 65535), (65535, 65535), (65535, 65535)),
    ((65535, 65535), (65535, 65535), (65535, 65535), (65535, 65535)),
    ((65535, 65535), (65535, 65535), (65535, 65535), (65535, 65535)),
)
"""$FEBE: what each item adds to HP and SP at each of its four levels; 65535 is no bonus."""

FIRST_ITEM: Final = 32
NO_BONUS: Final = 0xFFFF
