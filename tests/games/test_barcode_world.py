"""Tests for reading and building Barcode World cards."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.decoder.errors import BarcodeError
from maeyomi.games.barcode_world import (
    JOB_KEY,
    MAGICIAN,
    SPEED_KEY,
    WARRIOR,
    BarcodeWorldOrder,
    build_barcode_world,
    decode_barcode_world,
    strongest_barcode_world,
)
from maeyomi.models.constraint import Constraint

FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "barcode_world.json"
ANY: Constraint = Constraint.anything()


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


def fields(barcode: str) -> dict[str, int]:
    card = decode_barcode_world(barcode)
    job, speed, ability, number, strength, defence = card.traits
    fighter = card.kind is GameKind.FIGHTER
    return {
        "hp": card.value("WHP") // 100 if fighter else number,
        "st": card.value("WST") // 100 if fighter else strength,
        "df": card.value("WDF") // 100 if fighter else defence,
        "kind": card.ident,
        "job": job,
        "speed": speed,
        "ability": ability,
        "mp": card.value("WMP"),
        "pp": card.value("WPP"),
    }


@pytest.mark.parametrize("entry", recorded(), ids=lambda entry: str(entry["barcode"]))
def test_every_code_reads_as_the_game_itself_read_it_in_mame(entry: dict[str, object]) -> None:
    read = fields(str(entry["barcode"]))

    if read["kind"] < 5:
        assert read == {key: entry[key] for key in read}
    else:
        keys = ("kind", "hp", "st", "df", "job", "speed", "ability")
        assert {key: read[key] for key in keys} == {key: entry[key] for key in keys}


def test_the_strongest_barcode_battler_code_is_a_full_magician_with_capped_defence() -> None:
    read = fields("4994699095453")

    assert (read["hp"], read["st"], read["df"], read["mp"], read["pp"]) == (499, 146, 99, 10, 5)


def test_an_item_card_is_read_as_the_kind_the_card_is_printed_as() -> None:
    card = decode_barcode_world("0021909500408")

    assert (card.kind, card.ident, card.stats) == (GameKind.ITEM, 5, ())


def test_a_malformed_code_is_refused_before_it_is_read() -> None:
    with pytest.raises(BarcodeError):
        decode_barcode_world("4994699095450")


def test_a_fighter_is_built_with_exactly_the_numbers_and_choices_asked_for() -> None:
    order = BarcodeWorldOrder(
        WARRIOR,
        (Constraint.exactly(12300), Constraint.exactly(4500), Constraint.exactly(6700)),
        ((JOB_KEY, 3), (SPEED_KEY, 8)),
    )

    card = build_barcode_world(order)

    assert card is not None
    read = fields(card.barcode)
    assert (read["hp"], read["st"], read["df"], read["job"], read["speed"]) == (123, 45, 67, 3, 8)


def test_health_above_19900_needs_speed_5_and_a_9_in_the_hundreds() -> None:
    order = BarcodeWorldOrder(
        MAGICIAN,
        (Constraint.exactly(35900), Constraint.exactly(15000), Constraint.exactly(9900)),
    )

    card = build_barcode_world(order)

    assert card is not None
    read = fields(card.barcode)
    assert (read["hp"], read["st"], read["df"], read["speed"], read["mp"]) == (359, 150, 99, 5, 10)


def test_health_above_19900_that_does_not_end_in_900_builds_no_card() -> None:
    assert (
        build_barcode_world(BarcodeWorldOrder(WARRIOR, (Constraint.exactly(35000), ANY, ANY)))
        is None
    )


def test_a_defence_above_9900_needs_health_above_19900() -> None:
    order = BarcodeWorldOrder(WARRIOR, (Constraint.at_most(19900), ANY, Constraint.exactly(15000)))

    assert build_barcode_world(order) is None


def test_a_job_that_is_not_the_class_asked_for_builds_no_card() -> None:
    assert build_barcode_world(BarcodeWorldOrder(WARRIOR, (ANY, ANY, ANY), ((JOB_KEY, 8),))) is None


def test_the_strongest_card_is_a_magician_at_every_ceiling() -> None:
    card = strongest_barcode_world()

    read = fields(card.barcode)
    assert (read["hp"], read["st"], read["df"], read["mp"], read["pp"]) == (499, 199, 199, 10, 5)
