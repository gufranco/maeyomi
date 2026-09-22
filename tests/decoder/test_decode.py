"""Tests for the public decoding entry point."""

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.decoder.errors import CheckDigitError, InvalidLengthError
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType


def test_a_front_read_card_decodes_end_to_end() -> None:
    character = decode("0401207237501")

    assert character.read_type is ReadType.FRONT
    assert (character.hp, character.st, character.df) == (4000, 1200, 700)
    assert character.race is Race.AQUATIC
    assert character.character_class is not None


def test_a_back_read_card_decodes_end_to_end() -> None:
    character = decode("7310707558739")

    assert character.read_type is ReadType.BACK


def test_separators_are_tolerated() -> None:
    assert decode("0401-207-237501").barcode == "0401207237501"


def test_a_twelve_digit_code_is_rejected() -> None:
    with pytest.raises(InvalidLengthError):
        decode("040120723750")


def test_a_broken_check_digit_is_rejected() -> None:
    with pytest.raises(CheckDigitError):
        decode("0401207237509")


def test_the_decoded_barcode_is_carried_on_the_result() -> None:
    assert decode("0401207237501").barcode == "0401207237501"
