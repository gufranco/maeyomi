"""Tests for the strongest card the device can be handed."""

from barcode_battler.decoder.decode import decode
from barcode_battler.generator.cheat import (
    CHEAT_CODES,
    DEFAULT_CHEAT_NAME,
    accepted_codes,
    strongest_card,
)
from barcode_battler.generator.front_solver import MAX_HP_DISPLAY, MAX_STAT_DISPLAY
from barcode_battler.generator.quarantine import takes_quarantined_branch
from barcode_battler.models.character_class import CharacterClass
from barcode_battler.models.read_type import ReadType


def test_the_strongest_card_decodes_to_what_it_claims() -> None:
    card = strongest_card()

    assert decode(card.barcode) == card.character


def test_the_strongest_card_reaches_every_ceiling_it_can() -> None:
    character = strongest_card().character

    assert character.hp == MAX_HP_DISPLAY
    assert max(character.st, character.df) == MAX_STAT_DISPLAY


def test_no_other_front_read_fighter_has_more_strength_and_defence_together() -> None:
    character = strongest_card().character

    assert character.st + character.df == 44400


def test_the_strongest_card_never_rests_on_an_unresolved_branch() -> None:
    assert not takes_quarantined_branch(strongest_card().barcode)


def test_the_strongest_card_is_a_magician_with_its_attack_doubled() -> None:
    character = strongest_card().character

    assert character.read_type is ReadType.FRONT
    assert character.character_class is CharacterClass.MAGICIAN
    assert character.special.description == "own attack doubled"


def test_the_card_carries_the_name_it_is_given() -> None:
    assert strongest_card("Grandma").name == "Grandma"


def test_the_card_has_a_silly_name_by_default() -> None:
    assert strongest_card().name == DEFAULT_CHEAT_NAME


def test_every_cheat_code_is_written_without_spaces_in_capitals() -> None:
    assert CHEAT_CODES
    assert all(code == code.upper().replace(" ", "") for code in CHEAT_CODES)


def test_the_card_s_own_barcode_opens_it_too() -> None:
    assert strongest_card().barcode in accepted_codes()


def test_every_written_code_is_accepted() -> None:
    assert accepted_codes() >= CHEAT_CODES
