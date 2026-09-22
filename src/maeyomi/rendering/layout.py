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
from typing import Final

from maeyomi.rendering.calibration import FOOT_BAND_MM

A4_WIDTH_MM: Final = 210.0
A4_HEIGHT_MM: Final = 297.0
CARD_WIDTH_MM: Final = 63.5
CARD_HEIGHT_MM: Final = 88.9
"""The printed size of one card: poker size, which sleeves and guillotines fit.

Epoch never published the size of its own cards and no collector page records
it, so this is a choice rather than a reproduction. Changing these two numbers
moves everything else: the grid, the gutters, the marks and the fit check are
all derived from them.
"""

POKER_CARD_WIDTH_MM: Final = CARD_WIDTH_MM
POKER_CARD_HEIGHT_MM: Final = CARD_HEIGHT_MM
DEFAULT_MARGIN_MM: Final = 3.0
DEFAULT_BLEED_MM: Final = 1.5
DEFAULT_GUTTER_MM: Final = 2 * DEFAULT_BLEED_MM
MARK_BAND_MM: Final = FOOT_BAND_MM
"""What the marks need at the foot. Nothing is printed above the grid."""

CUT_MARK_LENGTH_MM: Final = 2.0
"""How far a corner tick reaches past a card, and so past the bottom row."""

MARK_CLEARANCE_MM: Final = 1.5
"""Kept between the lowest cut mark and the highest ink in the band below it."""

EDGE_CLEARANCE_MM: Final = 5.0
"""How close a trim line may come to the paper, which most printers can reach."""
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
    def print_shop(cls) -> SheetLayout:
        """One card per page, sized to the card plus the bleed a printer asks for."""
        bleed = PRINT_SHOP_BLEED_MM
        return cls(
            page_width_mm=CARD_WIDTH_MM + 2 * bleed,
            page_height_mm=CARD_HEIGHT_MM + 2 * bleed,
            margin_mm=0.0,
            gutter_mm=0.0,
            bleed_mm=bleed,
            marks=False,
        )

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
            self.page_height_mm - self._head_mm - self._foot_mm,
            self.margin_mm,
            self.card_height_mm,
            self.gutter_mm,
        )

    def _bottom_mm(self) -> float:
        """Where the lowest row starts.

        With marks on, the grid sits directly above their band rather than
        centred in what is left. Centring would hand half the spare room to the
        foot, which already has the widest band on the page, and take it from
        the head, where the top row would then be trimmed by a printer that
        cannot reach the paper's edge.
        """
        free = self.page_height_mm - self._head_mm - self._foot_mm
        if not self.marks:
            return self._foot_mm + _origin(free, self.rows, self.card_height_mm, self.gutter_mm)
        return self._foot_mm + CUT_MARK_LENGTH_MM + MARK_CLEARANCE_MM

    @property
    def _head_mm(self) -> float:
        """Nothing is printed above the grid, so the grid may reach the margin."""
        return 0.0

    @property
    def _foot_mm(self) -> float:
        """The strip kept clear below the grid, where the ruler is printed."""
        return FOOT_BAND_MM if self.marks else 0.0

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
        top = self._bottom_mm()
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
