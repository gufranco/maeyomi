"""Tests for random sheets on any device."""

import pytest

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.datach.dbz import DbzCard, DbzKind
from maeyomi.datach.dbz_reader import Readability, readability
from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_reader import printable
from maeyomi.double.card import DoubleCard
from maeyomi.generator.device_random import random_for
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.models.race import Race
from maeyomi.registry import read_as

RANGES = CardRequest(
    hp=Constraint.between(1000, 10000),
    st=Constraint.between(100, 3000),
    df=Constraint.between(100, 3000),
)
DBZ_RANGES = CardRequest(
    hp=Constraint.between(10000, 60000),
    st=Constraint.between(5000, 30000),
    df=Constraint.between(5000, 30000),
)
TEMPLATES = {Device.BB1: RANGES, Device.DOUBLE: RANGES, Device.DATACH_DBZ: DBZ_RANGES}


@pytest.mark.parametrize(
    ("device", "shape"),
    [(Device.BB1, FirstBattlerCard), (Device.DOUBLE, DoubleCard), (Device.DATACH_DBZ, DbzCard)],
)
def test_every_card_is_the_devices_own_reading_of_its_barcode(device: Device, shape: type) -> None:
    batch = random_for(device, 9, template=TEMPLATES[device], seed=7)

    assert len(batch.cards) == 9
    assert batch.shortfall == 0
    for card in batch.cards:
        assert isinstance(card.character, shape)
        assert read_as(device, card.barcode) == card.character


def test_a_dragon_ball_sheet_holds_fighters_inside_the_ranges() -> None:
    batch = random_for(Device.DATACH_DBZ, 9, template=DBZ_RANGES, seed=3)

    assert len(batch.cards) == 9
    for card in batch.cards:
        character = card.character
        assert isinstance(character, DbzCard)
        assert character.kind is not DbzKind.ITEM
        assert 10000 <= character.hp <= 60000
        assert 5000 <= character.bp <= 30000
        assert 5000 <= character.dp <= 30000


def test_a_dragon_ball_card_is_named_after_its_fighter() -> None:
    card = random_for(Device.DATACH_DBZ, 1, template=DBZ_RANGES, seed=3).cards[0]

    assert card.name.endswith(" 01")


def test_the_same_seed_gives_the_same_sheet() -> None:
    first = random_for(Device.BB1, 5, template=RANGES, seed=11)
    second = random_for(Device.BB1, 5, template=RANGES, seed=11)

    assert [card.barcode for card in first.cards] == [card.barcode for card in second.cards]


def test_a_first_barcode_battler_sheet_keeps_the_race_asked_for() -> None:
    template = CardRequest(race=Race.ANIMAL)

    batch = random_for(Device.BB1, 4, template=template, seed=5)

    assert all(
        isinstance(card.character, FirstBattlerCard) and card.character.race is Race.ANIMAL
        for card in batch.cards
    )


def test_the_second_barcode_battler_keeps_its_own_generator() -> None:
    batch = random_for(Device.BB2, 3, template=RANGES, seed=1)

    assert len(batch.cards) == 3


def test_a_field_the_device_cannot_read_is_named_rather_than_ignored() -> None:
    batch = random_for(Device.DATACH_DBZ, 3, template=CardRequest(race=Race.HUMAN), seed=1)

    assert batch.cards == ()
    assert batch.reason == "Datach Dragon Ball Z does not read race"


def test_ranges_nothing_can_meet_report_a_shortfall() -> None:
    template = CardRequest(hp=Constraint.between(99000, 99500), st=Constraint.between(0, 100))

    batch = random_for(Device.BB1, 2, template=template, seed=1, attempts_per_card=5)

    assert batch.shortfall == 2
    assert "produced 0 of 2" in batch.reason


def test_a_dragon_ball_sheet_holds_only_codes_the_game_reads_at_any_speed() -> None:
    batch = random_for(Device.DATACH_DBZ, 30, template=DBZ_RANGES, seed=9)

    assert all(readability(card.barcode) is Readability.READS for card in batch.cards)


def test_an_ultraman_club_sheet_holds_fighters_every_datach_reader_accepts() -> None:
    template = CardRequest(
        hp=Constraint.at_least(5000), st=Constraint.anything(), df=Constraint.anything()
    )

    batch = random_for(Device.DATACH_ULTRAMAN, 6, template=template, seed=3)

    assert len(batch.cards) == 6
    for card in batch.cards:
        assert isinstance(card.character, DatachCard)
        assert card.character.kind is GameKind.FIGHTER
        assert card.character.value("PW") >= 5000
        assert printable(card.barcode)


def test_an_ultraman_club_sheet_refuses_a_race() -> None:
    template = CardRequest(race=Race.HUMAN)

    batch = random_for(Device.DATACH_ULTRAMAN, 3, template=template, seed=3)

    assert batch.reason == "Datach Ultraman Club does not read race"
    assert batch.cards == ()


def test_a_barcode_world_sheet_draws_any_code_the_barcode_battler_reads() -> None:
    template = CardRequest(
        hp=Constraint.anything(), st=Constraint.anything(), df=Constraint.anything()
    )

    batch = random_for(Device.BARCODE_WORLD, 5, template=template, seed=4)

    assert len(batch.cards) == 5
    for card in batch.cards:
        assert isinstance(card.character, DatachCard)
        assert card.character.kind is GameKind.FIGHTER
