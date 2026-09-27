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
                "Two sources give index 9 and two give index 11. For 9: the DX column "
                "of every card list on wikiwiki.jp, and the note.com analysis by "
                "sakigomyway, `DX=⑩`, whose author printed test codes and entered them "
                "on a device. For 11: pre_reading in src/BarcodeRead.as, where index 11 "
                "is also the units digit of the special ability, and "
                "barcodebattler.net/page08.htm, `前読みは「⑫」`. Index 9 is kept because "
                "it is the only reading any source claims to have checked on hardware."
            ),
            revisit="On a test against physical hardware that compares initiative.",
        ),
        "high_hp_bonus_sets": Uncertainty(
            question=(
                "Above 20000 HP, which strength digits make a mechanical fighter's "
                "defence, and its hidden battle strength, gain a bonus?"
            ),
            decision=(
                "13, 29, 45, 61, 77 and 93 raise the displayed defence. 14, 30, 46, 62, "
                "78 and 94 raise it too, and add 10000 to the strength a fight uses. An "
                "animal mirrors the second set on its defence digits."
            ),
            evidence=(
                "barcodebattler.net/page21.htm reports a device showing 4994699095453 as "
                "14600 ST and 19900 DF while fighting with 24600 ST. The note.com "
                "analysis by sakigomyway, tested on a device, gives both sets and a "
                "table of battle values. src/BarcodeRead.as instead has one set, 13 plus "
                "multiples of 16, adding 10000 to both displayed stats, which reads that "
                "same card as 14600 ST and 9900 DF against what the device showed."
            ),
            revisit="On a hardware test of a card from each set.",
        ),
        "battle_stat_wrap": Uncertainty(
            question=("When a hidden battle stat passes one byte, is 256 or 255 subtracted?"),
            decision="256, per the note.com table; the generator never emits the branch.",
            evidence=(
                "The note.com analysis tabulates 62 as a battle strength of 600, which "
                "is 256 subtracted. barcodebattler.net/page21.htm says to subtract "
                "25500 above 25600, which gives 700. Only digits 62, 78 and 94 reach it."
            ),
            revisit="On a hardware test with strength digits 62, race 0 and HP above 20000.",
            blocks_generation=True,
        ),
        "animal_partner_set": Uncertainty(
            question=(
                "Above 20000 HP, do an animal's defence digits 13, 29, 45, 61, 77 or 93 "
                "raise its strength?"
            ),
            decision="No, per the note.com analysis; the generator never emits them.",
            evidence=(
                "The note.com analysis lists the partner bonus for an animal only under "
                "the second set. src/BarcodeRead.as raises both stats for the first set, "
                "and page21 does not say."
            ),
            revisit="On a hardware test with defence digits 45, race 1 and HP above 20000.",
            blocks_generation=True,
        ),
        "low_leading_item_read_type": Uncertainty(
            question=(
                "A code starting with 0 or 1 whose eighth digit is 5 to 9: when is it "
                "read from the front?"
            ),
            decision=(
                "As the simulator decides, when HP, ST and DF digits are all in bounds; "
                "the generator never emits a code the two rules classify differently."
            ),
            evidence=(
                "prepost_check in src/BarcodeRead.as and barcodebattler.net/page02.htm "
                "test all three stats. The note.com flowchart, tested on a device, "
                "reads 9 as always front, 5 and 6 as front when ST is 19 or less, and 7 "
                "and 8 as front when DF is 19 or less."
            ),
            revisit="On a hardware test of an HP item whose HP digits exceed 050.",
            blocks_generation=True,
        ),
        "job_six_magic_points": Uncertainty(
            question="Is job 6 a warrior or a magician when magic points are assigned?",
            decision="A warrior, starting with no magic points.",
            evidence=(
                "barcodebattler.net/page01.htm and the note.com analysis both give jobs "
                "0 to 6 as warriors. src/BarcodeRead.as tests `job > 6` in two places "
                "and `job >= 6` in one, so the simulator disagrees with itself."
            ),
            revisit="On a hardware test that casts a spell with a job 6 fighter.",
        ),
        "bb1_back_read_flag": Uncertainty(
            question=(
                "On the first Barcode Battler, does an enemy read from the back carry a flag?"
            ),
            decision=(
                "The check digit, as the note.com analysis reads it; the generator tunes "
                "the check digit to 0 and refuses a request that names an enemy's flag."
            ),
            evidence=(
                "The note.com analysis of the original device by sakigomyway gives the "
                "flag as 0 followed by the thirteenth digit. barcodebattler.co.uk, "
                "Original Barcode Battler technical info, Method 2, says no "
                "representation for the flag was found. No listed card is read from the "
                "back, so no transcription settles it."
            ),
            revisit="On a hardware test of an enemy code whose check digit is 5.",
            blocks_generation=True,
        ),
        "double_seven_read_race_and_speed": Uncertainty(
            question="What race and speed does the Double give a 7-read card?",
            decision=("Neither is read; the generator refuses a 7-read request that names either."),
            evidence=(
                '"BBIIダブルC0" on barcodebattler.net says the 7-read race is '
                "still under investigation and gives no speed. The 11 cards on the "
                "wikiwiki.jp 正伝3 list fit race = eighth digit mod 5, but the eighth "
                "digit is also the hundreds of the attack, and no source states the "
                "rule, so the fit is not used."
            ),
            revisit="On a Double, or a source that describes how it reads a 7-read race.",
            blocks_generation=True,
        ),
        "epoch_software_boxes": Uncertainty(
            question=(
                "How does the Barcode Battler II read the boxes of the dedicated card "
                "software, 4905040352606, 4905040352705 and 4905040352804?"
            ),
            decision="Refused with a named reason rather than read as ordinary codes.",
            evidence=(
                "barcodebattler.co.uk, Barcode Battler II technical info, lists them among "
                "the Epoch product barcodes the device reads differently, marked "
                '"Requires further testing". The two boxes it does give are read as heroes.'
            ),
            revisit="On a hardware test of each box.",
        ),
        "bb1_box_flag": Uncertainty(
            question="Is the first Barcode Battler's own box a hero, flag 18?",
            decision="Flag 18, as the note.com analysis gives it.",
            evidence=(
                "The note.com analysis of the original device lists the box as usable as "
                "the hero with 5200 HP, 1500 ST and 100 DF, and marks flag 18 with a "
                "question mark."
            ),
            revisit="On a hardware test that starts B1 mode with the box.",
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
        "dbz_emulated_refusals": Uncertainty(
            question=(
                "Why does Datach Dragon Ball Z, running in MAME, refuse a few valid codes "
                "whose digits decode to an ordinary card?"
            ),
            decision=(
                "Decoded by the rule like any other code. Generated codes are not "
                "filtered, because the refused codes share no digit pattern that could "
                "be tested for."
            ),
            evidence=(
                "Of 236 codes fed to the game's reader in MAME 0.289, 232 were accepted "
                "and every one decoded as this project's decoder predicts. 20158231, "
                "3623401959035, 5532403373177 and 6312422195214 were refused before any "
                "card was shown, in the routine at $B379 that normalises the bar widths "
                "the reader measured. That routine depends on how the emulated reader "
                "times the bars, which MAME models and a real reader may not."
            ),
            revisit=(
                "On a trace of $B379 for the four codes, or on a read with a physical Datach."
            ),
        ),
        "double_onsen_tamago": Uncertainty(
            question=(
                "Does the Double read 0600000905307, 温泉たまご in the 正伝4 list, as a "
                "6000 HP item or as armour?"
            ),
            decision=(
                "Read as the II reads it, a back-read single-use armour of 700 DF, because "
                "the Double reads the II's codes the II's way and no source says otherwise "
                "for this code."
            ),
            evidence=(
                "The 正伝4 精霊伝説 list on wikiwiki.jp gives 0600000905307 as an HP item "
                "worth 6000. The first Barcode Battler reads it that way. The II's read-type "
                "rule sends it to a back read, which gives armour worth 700 DF, and so does "
                "the Double's. The other 30 cards of the list agree with the Double's "
                "reading, 8 of them items whose unused numbers the list leaves blank."
            ),
            revisit="On a read of the card with a physical Double.",
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
