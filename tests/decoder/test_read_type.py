"""Tests for front-read against back-read discrimination."""

import pytest

from maeyomi.decoder.read_type import classify_read_type
from maeyomi.models.read_type import ReadType


def test_an_eight_digit_code_is_always_read_from_the_back() -> None:
    assert classify_read_type("49123456") is ReadType.BACK


@pytest.mark.parametrize("code", ["0401207237501", "1954840299829"])
def test_a_leading_zero_or_one_with_a_fighter_race_digit_is_front_read(code: str) -> None:
    assert classify_read_type(code) is ReadType.FRONT


def test_a_leading_zero_with_an_item_race_digit_falls_back_to_the_stat_bounds() -> None:
    assert classify_read_type("0000600602017") is ReadType.FRONT


def test_the_stat_bound_fallback_rejects_a_code_above_the_documented_ceilings() -> None:
    assert classify_read_type("0992020950000") is ReadType.BACK


@pytest.mark.parametrize("code", ["7310707558739", "3966666425071"])
def test_a_high_leading_digit_needs_the_nine_and_five_marker(code: str) -> None:
    assert classify_read_type(code) is ReadType.BACK


def test_a_high_leading_digit_with_the_marker_is_front_read() -> None:
    assert classify_read_type("2090000005004") is ReadType.FRONT
