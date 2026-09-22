"""Tests for the decoder error hierarchy."""

import pytest

from maeyomi.decoder.errors import (
    BarcodeError,
    CheckDigitError,
    InvalidCharacterError,
    InvalidLengthError,
    UnsupportedBarcodeError,
)


@pytest.mark.parametrize(
    "error",
    [
        InvalidLengthError(length=12),
        InvalidCharacterError(barcode="04012072375A1"),
        CheckDigitError(barcode="0401207237509", expected=1),
        UnsupportedBarcodeError(barcode="0401207237501", reason="test"),
    ],
)
def test_every_decoder_error_is_a_barcode_error(error: BarcodeError) -> None:
    assert isinstance(error, BarcodeError)


def test_invalid_length_names_the_supported_lengths() -> None:
    error = InvalidLengthError(length=12)

    assert "8 or 13" in str(error)
    assert "12" in str(error)


def test_check_digit_error_reports_the_digit_that_would_have_been_correct() -> None:
    error = CheckDigitError(barcode="0401207237509", expected=1)

    assert error.expected == 1
    assert "1" in str(error)


def test_unsupported_barcode_carries_its_reason() -> None:
    error = UnsupportedBarcodeError(barcode="0401207237501", reason="shifted read")

    assert "shifted read" in str(error)
