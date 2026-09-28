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
            decision=(
                "The race is the eighth digit less 5 when that digit is 5 or more, and "
                "unknown below; the speed is not read, and the generator refuses a 7-read "
                "request that names one."
            ),
            evidence=(
                '"BBIIダブルC0" on barcodebattler.net says the 7-read race is '
                "still under investigation and gives no speed. Post 484 of the 5ch "
                "thread mevius.5ch.net/test/read.cgi/toy/1226667612 reports the race as "
                "the eighth digit less 5, checked on the 正伝3 and 正伝4 enemy cards, and "
                "all 11 7-read cards on the wikiwiki.jp 正伝3 list fit it; every one has "
                "an eighth digit of 5 or more. No source gives a speed."
            ),
            revisit=("On a Double, or a source that covers an eighth digit below 5 or the speed."),
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
            question="Does the device offer a shifted back read, and when?",
            decision="Not implemented; only the aligned back read is supported.",
            evidence=(
                "post_reading in src/BarcodeRead.as takes a shift, but every C1 and C2 "
                "call in src/barcode2.as passes 0. The shift comes only from the "
                "L-BATTLE, L-POWER, R-BATTLE and R-POWER buttons on the C0 card-entry "
                "screen, value_shift in src/barcode2.as, and moves only a fighter's HP, "
                "ST and DF digits. barcodebattler.co.uk f1018 does not mention it. It is "
                "a button press, not a property of the card, so no card can carry it."
            ),
            revisit="On a hardware test of those buttons while a card is read in C0.",
        ),
        "back_read_flag_rule": Uncertainty(
            question="How does a back-read card's flag come from its digits?",
            decision=(
                "The simulator's bands on the ninth digit P: 0 to 3 give R, 4 to 7 give "
                "10 plus R, 8 and 9 give 20 plus R, R being the eleventh digit."
            ),
            evidence=(
                "barcodebattler.co.uk f1018 gives Flag = 10 * P + R and ignores values "
                "above 29, so the two agree only when P is 0: 9613953286318 is flag 23 "
                "by the bands and 83, ignored, by f1018. f1018 also carries a misplaced "
                "parenthesis in its ST formula and two conflicting Method 1 rejection "
                "rules. No card list read on a device has a back-read card that decides "
                "it: every back-read card on wikiwiki.jp is on the Double's page or has "
                "a wrong check digit."
            ),
            revisit="On a hardware read of a back-read code whose ninth digit is 1 to 9.",
        ),
        "c1_back_read_items": Uncertainty(
            question="Do C1 and C2 read weapon, protector and health cards differently?",
            decision="No; items read the same in every mode.",
            evidence=(
                "barcodebattler.co.uk f1018 drops the thousands: in C1 and C2 a weapon's "
                "ST is 100 * ((Q + 5) mod 10), a protector's DF 100 * ((P + 7) mod 10) "
                "and a health card's HP 1000 * floor(S / 4) + 100 * R, so "
                "2756244522799 is 17200 HP in C0 and 2700 in C1. The simulator rescales "
                "only the first card when it is a hero and leaves items as C0 reads them."
            ),
            revisit="On a hardware read of an item card in C1 or C2.",
        ),
        "c1_hero_flag": Uncertainty(
            question="Does a hero read in C1 or C2 keep its flag?",
            decision="Yes; the rescale changes HP, ST and DF only.",
            evidence=(
                "barcodebattler.co.uk f1018 sets Flag = 50 for a C1 or C2 hero; "
                "calc_c1_reading in src/BarcodeRead.as leaves the flag it read, so "
                "3951286607674 keeps flag 6."
            ),
            revisit="On a hardware read of a hero card in C1 or C2.",
        ),
        "short_back_read_job": Uncertainty(
            question="Can an eight-digit back-read card be a wizard?",
            decision="No; every eight-digit back-read fighter is a soldier, job 4.",
            evidence=(
                "barcodebattler.co.uk f1018 says a fighter is a wizard when its digit M "
                "is 7 or more, which on an EAN-8 is the first digit, so 90000003 would "
                "be a wizard. post_reading in src/BarcodeRead.as fixes the job at 4 for "
                "every eight-digit code."
            ),
            revisit="On a hardware read of an EAN-8 back-read fighter whose first digit is 7 to 9.",
        ),
    }
)
