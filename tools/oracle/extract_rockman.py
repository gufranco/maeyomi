"""Write Ryuusei no Rockman's Wave Card list from GBE+'s Wave Scanner notes.

Usage: uv run python tools/oracle/extract_rockman.py --notes PATH --out PATH

The notes are src/docs/technical/Wave_Scanner.txt in GBE+ at 05a05e93. They
list every Wave Card with its number, its twelve-digit barcode and its English
and Japanese names. The Wave Scanner sends only the last three Code 128 C
pairs to the game, so a card is kept as those six digits; a few barcodes in
the notes have their first six digits transposed, which changes nothing the
game receives.
"""

import argparse
import re
from pathlib import Path
from typing import Final

ROW: Final = re.compile(r"^(\S+-\d+)\s*\|\s*(\d{12})\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$")
KEPT: Final = slice(6, 12)
ESCAPED: Final = frozenset(range(0xFF01, 0xFF5F))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.write_text(render(args.notes.read_text(encoding="utf-8")), encoding="utf-8")


def render(notes: str) -> str:
    lines = [
        '"""The Wave Cards Ryuusei no Rockman reads through the Wave Scanner.',
        "",
        "Written from GBE+'s Wave Scanner notes by tools/oracle/extract_rockman.py;",
        "regenerate rather than edit. Each card is its number, the last six digits",
        "of its barcode, and its English and Japanese names.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"CARDS: Final[tuple[tuple[str, str, str, str], ...]] = {escaped(repr(cards(notes)))}",
        "",
    ]
    return "\n".join(lines)


def escaped(text: str) -> str:
    """Python source with full-width signs written as escapes, as a linter wants them."""
    return "".join(
        f"\\u{ord(character):04x}" if ord(character) in ESCAPED else character for character in text
    )


def cards(notes: str) -> tuple[tuple[str, str, str, str], ...]:
    return tuple(
        (found[1], found[2][KEPT], found[3], found[4])
        for line in notes.splitlines()
        if (found := ROW.match(line)) is not None
    )


if __name__ == "__main__":
    main()
