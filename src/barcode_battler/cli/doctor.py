"""Check that this machine can actually produce a card that works.

Most of what can go wrong here is invisible until a card is in someone's hand:
a font that did not resolve, so every Japanese line came out blank; a native
library that is missing, so nothing verified the barcode it printed; a palette
edited by eye, so two kinds print as the same grey. Each check below answers
one of those, by doing the thing rather than by asking whether it could be
done.

No check branches on the operating system, and no check can only fail. A check
that always reports a fault stops being read, which is worse than not having
it.
"""

import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.geometry import (
    NOMINAL_BAR_HEIGHT_MM,
    NOMINAL_MODULE_WIDTH_MM,
    BarcodeGeometry,
)
from barcode_battler.barcode.symbol import draw_symbol, symbol_size_mm
from barcode_battler.barcode.verify import decode_pdf
from barcode_battler.decoder.decode import decode
from barcode_battler.models.race import Race
from barcode_battler.official.catalogue import official_cards
from barcode_battler.products.japan import japanese_products
from barcode_battler.rendering.palette import audit_palette
from barcode_battler.rendering.text import JAPANESE_FONT, font_for

KNOWN_BARCODE: Final = "4902102072618"
"""A bottle of tea, back read, armour worth 2400 defence."""

KNOWN_DEFENCE: Final = 2400
KNOWN_RACE: Final = Race.ARMOUR
JAPANESE_SAMPLE: Final = "ぼうぐ"
LOW_SPACE_GB: Final = 1.0
BYTES_PER_GB: Final = 1024**3


class State(Enum):
    """How a single check came out."""

    OK = "ok"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class Finding:
    """One check, its verdict and what it saw."""

    name: str
    state: State
    detail: str


def report() -> tuple[Finding, ...]:
    """Every check, the machine first and then this package."""
    return machine() + package()


def worst(findings: tuple[Finding, ...]) -> State:
    """The verdict for a whole report, which is its worst finding.

    An empty report is refused rather than passed, because a check that did not
    run is a failed check and never a skipped one.
    """
    if not findings:
        message = "nothing was checked, so there is no verdict to give"
        raise ValueError(message)
    order = (State.FAIL, State.WARN, State.OK)
    states = {finding.state for finding in findings}
    return next(state for state in order if state in states)


def machine() -> tuple[Finding, ...]:
    """What this computer is, and whether it can show the report it is given."""
    return (_python(), _terminal(), _free_space())


def package() -> tuple[Finding, ...]:
    """Whether every part that has to be right to print a working card is."""
    return (
        _decoder(),
        _barcode(),
        _japanese_font(),
        _palette(),
        _official(),
        _supermarket(),
    )


def _python() -> Finding:
    """The interpreter running this, which decides every other answer."""
    version = ".".join(str(part) for part in sys.version_info[:3])
    return Finding("python", State.OK, f"{version} at {sys.executable}")


def _terminal() -> Finding:
    """Whether this terminal can show the Japanese half of every card."""
    encoding = sys.stdout.encoding or "unknown"
    try:
        JAPANESE_SAMPLE.encode(encoding)
    except LookupError, UnicodeEncodeError:
        return Finding(
            "terminal",
            State.WARN,
            f"{encoding} cannot print Japanese, so half of every card will show as ?",
        )
    return Finding("terminal", State.OK, f"{encoding} prints Japanese")


def _free_space() -> Finding:
    """Room for the PDFs, which are the whole point of running this."""
    free_gb = shutil.disk_usage(Path.cwd()).free / BYTES_PER_GB
    state = State.OK if free_gb >= LOW_SPACE_GB else State.WARN
    return Finding("free space", state, f"{free_gb:.1f} GB free here")


def _decoder() -> Finding:
    """Read a card whose answer is known, rather than trusting the port."""
    character = decode(KNOWN_BARCODE)
    if character.race is not KNOWN_RACE or character.df != KNOWN_DEFENCE:
        return Finding(
            "decoder",
            State.FAIL,
            f"{KNOWN_BARCODE} read as {character.race.name.lower()} with DF {character.df}, "
            f"expected {KNOWN_RACE.name.lower()} with DF {KNOWN_DEFENCE}",
        )
    return Finding(
        "decoder", State.OK, f"{KNOWN_BARCODE} reads as armour worth {KNOWN_DEFENCE} defence"
    )


def _barcode() -> Finding:
    """Draw a symbol and read it back, because the digits prove nothing."""
    geometry = BarcodeGeometry()
    width, height = symbol_size_mm(KNOWN_BARCODE, geometry)
    with TemporaryDirectory(prefix="barcode-battler-doctor-") as directory:
        path = Path(directory) / "symbol.pdf"
        canvas = Canvas(str(path), pagesize=(width * mm, height * mm))
        draw_symbol(canvas, KNOWN_BARCODE, x_mm=0, y_mm=0, geometry=geometry)
        canvas.save()
        try:
            found = decode_pdf(path)
        except (OSError, ValueError) as error:
            return Finding("barcode", State.FAIL, f"nothing could read the drawn symbol: {error}")
    if found != [KNOWN_BARCODE]:
        return Finding("barcode", State.FAIL, f"the drawn symbol read back as {found}")
    return Finding(
        "barcode",
        State.OK,
        f"drawn at {NOMINAL_MODULE_WIDTH_MM} mm per module and "
        f"{NOMINAL_BAR_HEIGHT_MM} mm tall, decoded back as {KNOWN_BARCODE}",
    )


def _japanese_font() -> Finding:
    """The font every card's Japanese half is set in."""
    chosen = font_for(JAPANESE_SAMPLE)
    if chosen != JAPANESE_FONT:
        return Finding(
            "japanese font",
            State.FAIL,
            f"Japanese would be set in {chosen}, not {JAPANESE_FONT}",
        )
    return Finding("japanese font", State.OK, f"{JAPANESE_FONT} is registered and selected")


def _palette() -> Finding:
    """Re-measure the colours rather than trusting that they were measured once."""
    failures = audit_palette()
    if failures:
        return Finding("palette", State.FAIL, "; ".join(failures))
    return Finding(
        "palette",
        State.OK,
        "every kind is distinguishable in colour, in grey and under all three deficiencies",
    )


def _official() -> Finding:
    """The transcribed Epoch cards, which ship inside the package."""
    return Finding("official cards", State.OK, f"{len(official_cards())} cards ready to print")


def _supermarket() -> Finding:
    """The curated shelf, which also ships inside the package."""
    return Finding("supermarket", State.OK, f"{len(japanese_products())} Japanese products")
