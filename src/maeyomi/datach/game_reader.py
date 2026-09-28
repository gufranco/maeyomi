"""How the Datach games after Dragon Ball Z read a barcode's bars.

Dragon Ball Z sorts widths into classes and refuses a code whose bars or
spaces come in fewer than three widths (see `dbz_reader`). The later games do
not: they scale every width against the widest one and count modules, and in
MAME Ultraman Club, SD Gundam Wars, Yu Yu Hakusho and J.League Super Top
Players all read 20158231, 5532403373177 and 6312422195214, three codes Dragon
Ball Z never reads. What they share with it is trouble with a code whose bars
or spaces are exactly 1, 2 and 4 modules wide. Swiped in Ultraman Club at
twelve speeds from 250 to 800 microseconds a module, six such codes, five of
them printed by Bandai, each failed at four to eight of the speeds, while two
codes outside that set read at all twelve.

A card this project makes is held to the stricter rule, the one every Datach
game accepted every time, so it reads in all of them.
"""

from maeyomi.datach.dbz_reader import (
    SPEED_DEPENDENT_WIDTHS,
    Readability,
    readability,
    width_classes,
)


def game_readability(code: str) -> Readability:
    """Whether a later Datach game reads a code at any swipe speed or only at some."""
    bars, spaces = width_classes(code)
    if SPEED_DEPENDENT_WIDTHS in {bars, spaces}:
        return Readability.SPEED_DEPENDENT
    return Readability.READS


def printable(code: str) -> bool:
    """Whether a code reads in every Datach game at every swipe speed measured."""
    return readability(code) is Readability.READS
