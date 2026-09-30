"""The tables Family Jockey 2 reads a barcode with.

Written from the game's ROM by tools/oracle/extract_famjock2.py; regenerate
rather than edit. A key table is ten rows of seven, one row per digit sum;
a box is the first ten digits of a Namco game's own barcode.
"""

from typing import Final

RACEHORSE_KEYS: Final = (
    (0, 1, 2, 3, 4, 5, 6),
    (1, 2, 3, 4, 5, 6, 7),
    (2, 3, 4, 5, 6, 7, 8),
    (3, 4, 5, 6, 7, 8, 9),
    (4, 5, 6, 7, 8, 9, 0),
    (5, 6, 7, 8, 9, 0, 1),
    (6, 7, 8, 9, 0, 1, 2),
    (7, 8, 9, 0, 1, 2, 3),
    (8, 9, 0, 1, 2, 3, 4),
    (9, 0, 1, 2, 3, 4, 5),
)
MARE_KEYS: Final = (
    (5, 6, 7, 8, 9, 0, 1),
    (6, 7, 8, 9, 0, 1, 2),
    (7, 8, 9, 0, 1, 2, 3),
    (8, 9, 0, 1, 2, 3, 4),
    (9, 0, 1, 2, 3, 4, 5),
    (0, 1, 2, 3, 4, 5, 6),
    (1, 2, 3, 4, 5, 6, 7),
    (2, 3, 4, 5, 6, 7, 8),
    (3, 4, 5, 6, 7, 8, 9),
    (4, 5, 6, 7, 8, 9, 0),
)
STALLION_KEYS: Final = (
    (0, 1, 2, 3, 4, 5, 6),
    (2, 3, 4, 5, 6, 7, 8),
    (4, 5, 6, 7, 8, 9, 0),
    (6, 7, 8, 9, 0, 1, 2),
    (8, 9, 0, 1, 2, 3, 4),
    (1, 2, 3, 4, 5, 6, 7),
    (3, 4, 5, 6, 7, 8, 9),
    (5, 6, 7, 8, 9, 0, 1),
    (7, 8, 9, 0, 1, 2, 3),
    (9, 0, 1, 2, 3, 4, 5),
)
BOXES: Final = (
    "4907892000",
    "4907892070",
    "4907892040",
    "4907892031",
    "4907892033",
    "4907892055",
    "4907892052",
)
