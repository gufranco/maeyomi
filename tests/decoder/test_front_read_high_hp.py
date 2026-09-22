"""Tests for the high-HP adjustment, including the two quarantined branches.

A front read can only reach the 20000 HP threshold when its third digit is 9,
because the leading digit is then 2 or more and the published marker rule
requires that digit to be 9 and the tenth digit to be 5. Every code here
therefore carries the marker.

Two of these assertions pin behaviour this project believes is a defect in the
reference simulator: a strength overflow test against 256 where the published
ceiling is 199, and a defence correction that reads from strength. They exist so
the decoder stays faithful and so a change cannot pass unnoticed. The generator
refuses to emit either branch; see `uncertainties.py`.
"""

from barcode_battler.decoder.decode import decode
from barcode_battler.decoder.front_read import DUAL_BONUS_VALUES
from barcode_battler.decoder.uncertainties import UNCERTAINTIES
from barcode_battler.models.race import Race
from barcode_battler.models.read_type import ReadType

MECHANICAL_PLAIN = "2091000045007"
MECHANICAL_OVERFLOW = "2099300045000"
ANIMAL_DUAL = "2091013145008"
ANIMAL_OVERFLOW = "2091093145004"


def test_every_code_used_here_is_genuinely_a_front_read_above_the_threshold() -> None:
    codes = [MECHANICAL_PLAIN, MECHANICAL_OVERFLOW, ANIMAL_DUAL, ANIMAL_OVERFLOW]

    decoded = [decode(code) for code in codes]

    assert {character.read_type for character in decoded} == {ReadType.FRONT}
    assert {character.hp for character in decoded} == {20900}


def test_a_mechanical_race_gains_one_hundred_on_strength_alone() -> None:
    character = decode(MECHANICAL_PLAIN)

    assert character.race is Race.MECHANICAL
    assert int(character.barcode[3:5]) not in DUAL_BONUS_VALUES
    assert (character.st, character.df) == (11000, 0)


def test_a_mechanical_race_strength_past_the_overflow_threshold_wraps() -> None:
    character = decode(MECHANICAL_OVERFLOW)

    assert int(character.barcode[3:5]) in DUAL_BONUS_VALUES
    assert (character.st, character.df) == (3800, 10000)


def test_an_animal_race_partner_in_the_dual_set_raises_both_stats() -> None:
    character = decode(ANIMAL_DUAL)

    assert character.race is Race.ANIMAL
    assert int(character.barcode[5:7]) in DUAL_BONUS_VALUES
    assert (character.st, character.df) == (11000, 21300)


def test_the_animal_overflow_branch_writes_defence_from_strength() -> None:
    character = decode(ANIMAL_OVERFLOW)

    assert character.race is Race.ANIMAL
    assert character.st == 11000
    assert character.df == -14500


def test_both_quarantined_branches_are_recorded_as_blocking_generation() -> None:
    blocking = {key for key, entry in UNCERTAINTIES.items() if entry.blocks_generation}

    assert blocking == {"race_one_overflow_target", "st_overflow_threshold"}
