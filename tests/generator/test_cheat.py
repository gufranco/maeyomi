"""Tests for the strongest card the device can be handed."""

from maeyomi.decoder.decode import decode
from maeyomi.generator.cheat import DEFAULT_CHEAT_NAME, strongest_card
from maeyomi.generator.front_solver import MAX_HP_DISPLAY, MAX_STAT_DISPLAY
from maeyomi.generator.quarantine import takes_quarantined_branch
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.read_type import ReadType


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
