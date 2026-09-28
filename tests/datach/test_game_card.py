"""Tests for the card a Datach game reads a barcode into."""

from maeyomi.datach.game_card import DatachCard, GameKind, GameStat
from maeyomi.models.device import Device


def test_a_card_hands_back_the_value_of_a_number_it_carries() -> None:
    card = DatachCard(
        barcode="0315424322677",
        game=Device.DATACH_ULTRAMAN,
        kind=GameKind.FIGHTER,
        ident=3,
        stats=(GameStat("PW", 7200), GameStat("UST", 6900)),
    )

    assert card.value("UST") == 6900


def test_a_card_reports_zero_for_a_number_it_does_not_carry() -> None:
    card = DatachCard(
        barcode="0315424322677", game=Device.DATACH_ULTRAMAN, kind=GameKind.ITEM, ident=33
    )

    assert card.value("PW") == 0
