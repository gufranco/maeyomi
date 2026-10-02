"""Write a Beena game's card list from MAME's Beena software list.

Usage: uv run python tools/oracle/extract_beena.py --listing PATH --software NAME --out PATH

MAME 0.289's hash/sega_beena_cart.xml lists each card game's cards, each with
its number and the twelve-bit value its stripes give the console; a test card
is listed the same way after the others. A value becomes the card's twelve bar
places, the lowest bit first, which is the order the places run along the card.
"""

import argparse
import re
from pathlib import Path
from typing import Final

CARD: Final = re.compile(
    r'<feature name="part_id" value="(?:Test )?Card (\d+)[^"]*"/>\s*'
    r'<feature name="barcode" value="0x([0-9a-f]+)"/>'
)
PLACES: Final = 12
HEX: Final = 16


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listing", type=Path, required=True)
    parser.add_argument("--software", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    listing = args.listing.read_text(encoding="utf-8")
    args.out.write_text(render(listing, args.software), encoding="utf-8")


def render(listing: str, software: str) -> str:
    lines = [
        f'"""The cards {title(listing, software)} reads.',
        "",
        "Written from MAME's Beena software list by tools/oracle/extract_beena.py;",
        "regenerate rather than edit. Each card is its number and its twelve bar",
        "places, 1 for a bar, in the order they run along the card.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"CARDS: Final[tuple[tuple[int, str], ...]] = {cards(listing, software)!r}",
        "",
    ]
    return "\n".join(lines)


def _entry(listing: str, software: str) -> str:
    found = re.search(rf'<software name="{re.escape(software)}".*?</software>', listing, re.DOTALL)
    return "" if found is None else found.group(0)


def title(listing: str, software: str) -> str:
    """The game's name as the list describes it."""
    found = re.search(r"<description>(.*?)</description>", _entry(listing, software))
    return "" if found is None else found.group(1)


def bars(value: int) -> str:
    """A value's twelve bar places, its lowest bit first."""
    return "".join(str(value >> place & 1) for place in range(PLACES))


def cards(listing: str, software: str) -> tuple[tuple[int, str], ...]:
    return tuple(
        (int(number), bars(int(value, HEX)))
        for number, value in CARD.findall(_entry(listing, software))
    )


if __name__ == "__main__":
    main()
