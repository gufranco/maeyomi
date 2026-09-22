"""Where cards sit on a printed sheet.

Sizes are millimetres throughout, because the output is a physical card that a
scanner has to read. The default card is poker sized, which is what card sleeves
and cutting guillotines are built for, and nine of them fit an A4 page.

Two things printers ask for shape this. Artwork that reaches the edge of a card
is drawn past the trim line, the bleed, so a cut that lands a fraction off still
finds ink rather than white paper. And cards are set apart by a gutter wide
enough to hold both neighbours' bleed, so each card is cut on its own line
instead of sharing one with the card beside it.

`print_shop()` is the other shape the same cards take: one card per page, sized
to the card plus its bleed, which is what a commercial printer's own
instructions ask for.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final


class CardOrientation(Enum):
    """Which way round a card is printed."""

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

    @property
    def size_mm(self) -> tuple[float, float]:
        """The width and height of a card in this orientation."""
        if self is CardOrientation.LANDSCAPE:
            return (ID1_LONG_MM, ID1_SHORT_MM)
        return (ID1_SHORT_MM, ID1_LONG_MM)


A4_WIDTH_MM: Final = 210.0
A4_HEIGHT_MM: Final = 297.0
ID1_LONG_MM: Final = 85.60
ID1_SHORT_MM: Final = 53.98
"""The ISO/IEC 7810 ID-1 card, which is the size of a bank card."""

POKER_CARD_WIDTH_MM: Final = ID1_SHORT_MM
POKER_CARD_HEIGHT_MM: Final = ID1_LONG_MM
DEFAULT_MARGIN_MM: Final = 5.0
DEFAULT_BLEED_MM: Final = 2.0
DEFAULT_GUTTER_MM: Final = 2 * DEFAULT_BLEED_MM
MARK_BAND_MM: Final = 11.0
"""Height kept clear above and below the grid for the ruler and the note.

The cut marks live there too. Without it the grid centres on the page and the
marks land on the cards.
"""

PRINT_SHOP_BLEED_MM: Final = 3.0
"""The bleed commercial printers ask for, and the one `print_shop()` uses.

The sheet layout uses less, because a gutter wide enough for two 3 mm bleeds
costs a whole column on A4 and takes the page from nine cards to four.
"""


@dataclass(frozen=True, slots=True)
class SheetLayout:
    """A grid of cards on one page size."""

    page_width_mm: float = A4_WIDTH_MM
    page_height_mm: float = A4_HEIGHT_MM
    card_width_mm: float = POKER_CARD_WIDTH_MM
    card_height_mm: float = POKER_CARD_HEIGHT_MM
    margin_mm: float = DEFAULT_MARGIN_MM
    gutter_mm: float = DEFAULT_GUTTER_MM
    bleed_mm: float = DEFAULT_BLEED_MM
    marks: bool = True

    @classmethod
    def of(cls, orientation: CardOrientation) -> SheetLayout:
        """A sheet of cards in the given orientation."""
        width, height = orientation.size_mm
        return cls(card_width_mm=width, card_height_mm=height)

    @classmethod
    def print_shop(cls, orientation: CardOrientation = CardOrientation.PORTRAIT) -> SheetLayout:
        """One card per page, sized to the card plus the bleed a printer asks for."""
        bleed = PRINT_SHOP_BLEED_MM
        width, height = orientation.size_mm
        return cls(
            page_width_mm=width + 2 * bleed,
            page_height_mm=height + 2 * bleed,
            card_width_mm=width,
            card_height_mm=height,
            margin_mm=0.0,
            gutter_mm=0.0,
            bleed_mm=bleed,
            marks=False,
        )

    @property
    def orientation(self) -> CardOrientation:
        """Which way round these cards are."""
        if self.card_width_mm > self.card_height_mm:
            return CardOrientation.LANDSCAPE
        return CardOrientation.PORTRAIT

    def __post_init__(self) -> None:
        """Reject a grid that cannot be printed."""
        if self.margin_mm < 0 or self.gutter_mm < 0:
            message = f"margin and gutter must not be negative, got {self.margin_mm}"
            raise ValueError(message)
        if self.columns < 1 or self.rows < 1:
            message = (
                f"a card of {self.card_width_mm} by {self.card_height_mm} mm does not fit "
                f"a page of {self.page_width_mm} by {self.page_height_mm} mm "
                f"with a {self.margin_mm} mm margin"
            )
            raise ValueError(message)

    @property
    def columns(self) -> int:
        """How many cards fit across the page."""
        return _fit(self.page_width_mm, self.margin_mm, self.card_width_mm, self.gutter_mm)

    @property
    def rows(self) -> int:
        """How many cards fit down the page, outside the bands the marks need."""
        return _fit(
            self.page_height_mm - 2 * self._band_mm,
            self.margin_mm,
            self.card_height_mm,
            self.gutter_mm,
        )

    @property
    def _band_mm(self) -> float:
        """The strip kept clear at the head and the foot of the page."""
        return MARK_BAND_MM if self.marks else 0.0

    @property
    def cards_per_page(self) -> int:
        """How many cards one sheet holds."""
        return self.columns * self.rows

    def page_count(self, card_count: int) -> int:
        """How many sheets a batch of cards needs."""
        return -(-card_count // self.cards_per_page)

    def positions(self) -> list[tuple[float, float]]:
        """Lower left corner of every card slot, in reading order."""
        left = _origin(self.page_width_mm, self.columns, self.card_width_mm, self.gutter_mm)
        top = self._band_mm + _origin(
            self.page_height_mm - 2 * self._band_mm,
            self.rows,
            self.card_height_mm,
            self.gutter_mm,
        )
        step_x = self.card_width_mm + self.gutter_mm
        step_y = self.card_height_mm + self.gutter_mm
        return [
            (left + column * step_x, top + (self.rows - 1 - row) * step_y)
            for row in range(self.rows)
            for column in range(self.columns)
        ]


def _fit(page_mm: float, margin_mm: float, card_mm: float, gutter_mm: float) -> int:
    """How many cards fit along one axis inside the margins."""
    usable = page_mm - 2 * margin_mm
    if usable < card_mm:
        return 0
    return int((usable + gutter_mm) // (card_mm + gutter_mm))


def _origin(page_mm: float, count: int, card_mm: float, gutter_mm: float) -> float:
    """Where the centred grid starts along one axis."""
    used = count * card_mm + (count - 1) * gutter_mm
    return (page_mm - used) / 2
