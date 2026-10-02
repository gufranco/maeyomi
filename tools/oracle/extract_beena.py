"""Write a stripe card game's card list from one of MAME's software lists.

Usage: uv run python tools/oracle/extract_beena.py --listing PATH --software NAME --places N --out PATH

MAME 0.289's hash/sega_beena_cart.xml lists each Beena card game's cards, each
with its number and the twelve-bit value its stripes give the console; a test
card is listed the same way after the others. hash/tvochken.xml lists TV
Ocha-Ken's cards the same way, with sixteen-bit values. A value becomes the
card's bar places, the lowest bit first, which is the order the places run
along the card.
"""

import argparse
import re
from pathlib import Path
from typing import Final

CARD: Final = re.compile(
    r'<feature name="part_id" value="(?:Test )?Card (\d+)[^"]*"/>\s*'
    r'<feature name="barcode" value="0x([0-9a-f]+)"/>'
)
PLACES: Final = (12, 16)
HEX: Final = 16


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listing", type=Path, required=True)
    parser.add_argument("--software", required=True)
    parser.add_argument("--places", type=int, choices=PLACES, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    listing = args.listing.read_text(encoding="utf-8")
    args.out.write_text(render(listing, args.software, args.places), encoding="utf-8")


def render(listing: str, software: str, places: int) -> str:
    lines = [
        f'"""The cards {title(listing, software)} reads.',
        "",
        f"Written from MAME's hash/{list_name(listing)}.xml by tools/oracle/extract_beena.py;",
        f"regenerate rather than edit. Each card is its number and its {places} bar",
        "places, 1 for a bar, in the order they run along the card.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"CARDS: Final[tuple[tuple[int, str], ...]] = {cards(listing, software, places)!r}",
        "",
    ]
    return "\n".join(lines)


def _entry(listing: str, software: str) -> str:
    found = re.search(rf'<software name="{re.escape(software)}".*?</software>', listing, re.DOTALL)
    return "" if found is None else found.group(0)


def list_name(listing: str) -> str:
    """The name MAME gives the software list."""
    found = re.search(r'<softwarelist name="([^"]+)"', listing)
    return "" if found is None else found.group(1)


def title(listing: str, software: str) -> str:
    """The game's name as the list describes it."""
    found = re.search(r"<description>(.*?)</description>", _entry(listing, software))
    return "" if found is None else found.group(1)


def bars(value: int, places: int) -> str:
    """A value's bar places, its lowest bit first."""
    return "".join(str(value >> place & 1) for place in range(places))


def cards(listing: str, software: str, places: int) -> tuple[tuple[int, str], ...]:
    return tuple(
        (int(number), bars(int(value, HEX), places))
        for number, value in CARD.findall(_entry(listing, software))
    )


if __name__ == "__main__":
    main()
