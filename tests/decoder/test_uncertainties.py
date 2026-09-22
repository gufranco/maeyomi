"""Tests for the register of behaviours the references disagree about."""

from maeyomi.decoder.uncertainties import UNCERTAINTIES, Uncertainty


def test_the_register_is_not_empty() -> None:
    assert UNCERTAINTIES


def test_every_entry_states_a_question_a_decision_and_a_revisit_condition() -> None:
    incomplete = [
        key
        for key, entry in UNCERTAINTIES.items()
        if not (entry.question and entry.decision and entry.evidence and entry.revisit)
    ]

    assert incomplete == []


def test_the_front_read_speed_digit_is_recorded() -> None:
    entry = UNCERTAINTIES["front_read_speed_digit"]

    assert isinstance(entry, Uncertainty)
    assert "9" in entry.decision


def test_the_generator_blocking_entries_are_flagged() -> None:
    blocking = {key for key, entry in UNCERTAINTIES.items() if entry.blocks_generation}

    assert blocking == {"race_one_overflow_target", "st_overflow_threshold"}


def test_the_overflow_threshold_is_not_described_as_unreachable() -> None:
    evidence = UNCERTAINTIES["st_overflow_threshold"].evidence

    assert "unreachable" not in evidence
    assert "261" in evidence
