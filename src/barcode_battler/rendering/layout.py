"""Where cards sit on a printed sheet.

Sizes are millimetres throughout, because the output is a physical card that a
scanner has to read. The default card is poker sized, which is what card sleeves
and cutting guillotines are built for, and nine of them fit an A4 page.
"""

from dataclasses import dataclass
from typing import Final

A4_WIDTH_MM: Final = 210.0
A4_HEIGHT_MM: Final = 297.0
POKER_CARD_WIDTH_MM: Final = 63.5
POKER_CARD_HEIGHT_MM: Final = 88.9
DEFAULT_MARGIN_MM: Final = 8.0
DEFAULT_GUTTER_MM: Final = 0.0


@dataclass(frozen=True, slots=True)
class SheetLayout:
    """A grid of cards on one page size."""

    page_width_mm: float = A4_WIDTH_MM
    page_height_mm: float = A4_HEIGHT_MM
    card_width_mm: float = POKER_CARD_WIDTH_MM
    card_height_mm: float = POKER_CARD_HEIGHT_MM
    margin_mm: float = DEFAULT_MARGIN_MM
    gutter_mm: float = DEFAULT_GUTTER_MM

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
        """How many cards fit down the page."""
        return _fit(self.page_height_mm, self.margin_mm, self.card_height_mm, self.gutter_mm)

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
        top = _origin(self.page_height_mm, self.rows, self.card_height_mm, self.gutter_mm)
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
