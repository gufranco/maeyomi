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
                "a test against physical hardware that compares initiative."
            ),
        ),
        "race_one_overflow_target": Uncertainty(
            question=(
                "In the race 1 high-HP branch, does the overflow correction write to "
                "DF from ST, or to DF from DF?"
            ),
            decision=(
                "DF = DF - 255, diverging from the simulator; the generator still never "
                "emits the branch."
            ),
            evidence=(
                "src/BarcodeRead.as reads `barcode_data.df = barcode_data.st - 255`. The "
                "branch is only reached with DF digits 61, 77 or 93, where ST is at most "
                "199, so the simulator's line always yields a negative DF, from -15500 to "
                "-5600. A device stores DF unsigned and cannot display a negative value, "
                "so the verbatim line is wrong whatever the hardware does. The race 0 "
                "branch corrects the field it is correcting, and VITIMan/maeyomi-"
                "engine copies the line with the comment `sounds strange, should be DF?`. "
                "No transcribed card among 577 reaches the branch, so the corrected value "
                "is the most plausible reading rather than a confirmed one."
            ),
            revisit=(
                "On a test against physical hardware with a barcode whose DF "
                "digits are 61, 77 or 93, race digit 1 and hit points of 20000 or more."
            ),
            blocks_generation=True,
        ),
        "st_overflow_threshold": Uncertainty(
            question=(
                "When a mechanical fighter's ST overflows, is 255 subtracted, as the "
                "simulator does, or 256, as a one-byte register wrapping would?"
            ),
            decision="255, as the simulator does; the generator never emits the branch.",
            evidence=(
                "src/BarcodeRead.as tests `st > 256` and subtracts 255. The branch is "
                "reachable: ST digits 61, 77 and 93 are in the dual bonus set, collect "
                "two bonuses of 100, and reach 261, 277 and 293. No reachable value equals "
                "256, so the threshold's exact form does not matter; only the subtrahend "
                "does, and it moves the printed ST by 100. barcodebattler.net/page10.htm "
                "shows the device comparing against a random byte from 0 to 255, which "
                "fits a one-byte register and therefore 256, but does not settle it. The "
                "handheld ran on an NEC uPD75 microcontroller whose firmware has never "
                "been dumped, so no emulator can answer it. No transcribed card among 577 "
                "reaches the branch."
            ),
            revisit=(
                "On a test against physical hardware with a barcode whose ST "
                "digits are 61, 77 or 93, race digit 0 and hit points of 20000 or more."
            ),
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
            revisit="On a test against physical hardware.",
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
