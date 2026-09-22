"""Tests for the EAN check digit the device verifies before reading a barcode."""

import json
import pathlib

import pytest

from barcode_battler.decoder.check_digit import expected_check_digit

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures"


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("040120723750", 1),
        ("034101138450", 6),
        ("195484029982", 9),
        ("000060060201", 7),
    ],
)
def test_thirteen_digit_check_digit(body: str, expected: int) -> None:
    assert expected_check_digit(body) == expected


def test_an_eight_digit_body_is_left_padded_to_thirteen() -> None:
    padded = expected_check_digit("00000" + "1234567")

    assert expected_check_digit("1234567") == padded


def test_a_full_code_may_be_passed_and_its_last_digit_is_ignored() -> None:
    assert expected_check_digit("0401207237501") == 1
    assert expected_check_digit("0401207237509") == 1


def test_every_real_card_in_the_simulator_corpus_carries_a_valid_check_digit() -> None:
    corpus = json.loads((FIXTURES / "simulator_corpus.json").read_text(encoding="utf-8"))

    invalid = [
        card["barcode"]
        for card in corpus["cards"]
        if len(card["barcode"]) in (8, 13)
        and expected_check_digit(card["barcode"]) != int(card["barcode"][-1])
    ]

    assert invalid == []


@pytest.mark.parametrize("code", ["", "12345", "abcdefghijklm"])
def test_a_non_numeric_or_wrong_length_body_is_rejected(code: str) -> None:
    with pytest.raises(ValueError, match="digits"):
        expected_check_digit(code)
