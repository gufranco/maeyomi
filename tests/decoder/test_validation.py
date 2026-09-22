"""Tests for barcode acceptance, the gate every read passes through first."""

import pytest

from barcode_battler.decoder.errors import (
    CheckDigitError,
    InvalidCharacterError,
    InvalidLengthError,
)
from barcode_battler.decoder.validation import validate_barcode


@pytest.mark.parametrize("code", ["0401207237501", "49123456"])
def test_a_valid_code_is_returned_unchanged(code: str) -> None:
    assert validate_barcode(code) == code


def test_surrounding_whitespace_and_separators_are_stripped() -> None:
    assert validate_barcode(" 0401207 237501 ") == "0401207237501"


@pytest.mark.parametrize("length", [7, 9, 12, 14])
def test_an_unsupported_length_is_rejected(length: int) -> None:
    with pytest.raises(InvalidLengthError) as caught:
        validate_barcode("1" * length)

    assert caught.value.length == length


def test_a_twelve_digit_upc_a_code_is_rejected_rather_than_padded() -> None:
    with pytest.raises(InvalidLengthError):
        validate_barcode("040120723750")


def test_a_non_digit_is_rejected() -> None:
    with pytest.raises(InvalidCharacterError):
        validate_barcode("04012072375A1")


def test_a_wrong_check_digit_reports_the_correct_one() -> None:
    with pytest.raises(CheckDigitError) as caught:
        validate_barcode("0401207237509")

    assert caught.value.expected == 1
