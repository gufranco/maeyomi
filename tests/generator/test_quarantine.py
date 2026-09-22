"""Tests for the refusal to emit a code whose behaviour is unresolved."""

import pytest

from barcode_battler.generator.quarantine import takes_quarantined_branch


@pytest.mark.parametrize("code", ["2099300045000", "2091093145004"])
def test_a_code_reaching_an_overflow_branch_is_quarantined(code: str) -> None:
    assert takes_quarantined_branch(code)


@pytest.mark.parametrize("code", ["2091000045007", "2091013145008", "0401207237501"])
def test_an_ordinary_code_is_not_quarantined(code: str) -> None:
    assert not takes_quarantined_branch(code)


def test_a_back_read_code_is_never_quarantined() -> None:
    assert not takes_quarantined_branch("7310707558739")


def test_a_race_that_takes_no_bonus_is_never_quarantined() -> None:
    assert not takes_quarantined_branch("2099399945004")
