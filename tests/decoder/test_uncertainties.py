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

    assert blocking == {
        "battle_stat_wrap",
        "animal_partner_set",
        "low_leading_item_read_type",
        "bb1_back_read_flag",
    }


def test_the_wrap_entry_names_both_subtrahends_it_chose_between() -> None:
    evidence = UNCERTAINTIES["battle_stat_wrap"].evidence

    assert "256" in evidence
    assert "25500" in evidence


def test_the_bonus_set_entry_cites_the_card_a_device_showed() -> None:
    assert "4994699095453" in UNCERTAINTIES["high_hp_bonus_sets"].evidence
