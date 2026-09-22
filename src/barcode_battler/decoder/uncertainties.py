"""Behaviours the available references disagree about.

Each entry names the question, the behaviour this project chose, the evidence
behind the choice, and what would settle it. An entry flagged
`blocks_generation` is a branch the decoder reproduces faithfully but the
generator refuses to emit, so an unresolved question can never reach a printed
card.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final


@dataclass(frozen=True, slots=True)
class Uncertainty:
    """One open question about the device's behaviour."""

    question: str
    decision: str
    evidence: str
    revisit: str
    blocks_generation: bool = False


UNCERTAINTIES: Final[Mapping[str, Uncertainty]] = MappingProxyType(
    {
        "front_read_speed_digit": Uncertainty(
            question="Which digit of a front-read code carries speed?",
            decision="Digit index 9.",
            evidence=(
                "pre_reading in src/BarcodeRead.as reads index 11, which is the units "
                "digit of the two-digit special ability at indices 10 and 11, leaving "
                "index 9 unread. The DX column of every card list on wikiwiki.jp "
                "matches index 9 and never index 11. The simulator never displays "
                "speed, so the value is weakly exercised there."
            ),
            revisit=(
                "When the table image on barcodebattler.net/page08.htm is read, or on "
                "the first test against physical hardware."
            ),
        ),
        "race_one_overflow_target": Uncertainty(
            question=(
                "In the race 1 high-HP branch, does the overflow correction write to "
                "DF from ST, or to DF from DF?"
            ),
            decision="Ported verbatim as DF = ST - 255; the generator never emits it.",
            evidence=(
                "src/BarcodeRead.as reads `barcode_data.df = barcode_data.st - 255` "
                "while every sibling branch adjusts the field it is correcting. No "
                "fixture reaches the branch, so neither reading can be confirmed."
            ),
            revisit="On the first test against physical hardware.",
            blocks_generation=True,
        ),
        "st_overflow_threshold": Uncertainty(
            question="Why is the ST overflow test 256 when the documented ST ceiling is 199?",
            decision="Ported verbatim as ST > 256; the generator never emits it.",
            evidence=(
                "src/BarcodeRead.as tests `st > 256`. barcodebattler.net/page01.htm "
                "publishes a front-read ST ceiling of 19900, which is 199 internal "
                "units, so the threshold is unreachable by the arithmetic that "
                "precedes it and its intent cannot be inferred."
            ),
            revisit="On the first test against physical hardware.",
            blocks_generation=True,
        ),
        "upc_a_twelve_digits": Uncertainty(
            question="Does the hardware left-pad a 12-digit UPC-A code to 13 digits?",
            decision="Rejected, matching the simulator.",
            evidence=(
                "check_barcode in src/BarcodeRead.as accepts only 8 and 13 digits, yet "
                "the simulator's own card XML contains two 12-digit entries, which it "
                "would therefore refuse to read."
            ),
            revisit="On the first test against physical hardware.",
        ),
        "shifted_back_read": Uncertainty(
            question="What are the shift semantics for a deliberately misaligned read?",
            decision="Not implemented; only the aligned back read is supported.",
            evidence=(
                "post_reading in src/BarcodeRead.as takes a shift parameter used by the "
                "C1 and C2 game modes. Card generation never needs it, and no fixture "
                "exercises it."
            ),
            revisit="If a card list is found whose values only reproduce under a shift.",
        ),
    }
)
