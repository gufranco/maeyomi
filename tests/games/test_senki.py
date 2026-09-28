"""Tests for reading and building Barcode Battler Senki cards."""

import json
import random
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.decoder.errors import BarcodeError
from maeyomi.games.barcode_world import JOB_KEY, WARRIOR, decode_barcode_world
from maeyomi.games.senki import (
    SOUND_TEST,
    SenkiOrder,
    black_store_stats,
    build_senki,
    decode_senki,
    strongest_senki,
)
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "barcode_battler_senki.json"
BLACK_STORE = Path(__file__).parent.parent / "fixtures" / "oracle" / "senki_black_store.json"
ANY: Constraint = Constraint.anything()
FIGHTER_KEYS = ("hp", "st", "df", "kind", "job", "speed", "ability", "mp", "pp")
ITEM_KEYS = ("st", "df", "kind", "job", "speed", "ability")
MAGICIAN_JOB = 9


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


def fields(barcode: str) -> dict[str, int]:
    card = decode_senki(barcode)
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


@pytest.mark.parametrize(
    "entry",
    [entry for entry in recorded() if not entry.get("sound_test")],
    ids=lambda entry: str(entry["barcode"]),
)
def test_every_code_reads_as_the_game_itself_read_it_in_mame(entry: dict[str, object]) -> None:
    read = fields(str(entry["barcode"]))

    keys = FIGHTER_KEYS if read["kind"] < 5 else ITEM_KEYS
    assert {key: read[key] for key in keys} == {key: entry[key] for key in keys}


def test_the_interface_box_code_opens_the_sound_test_instead_of_making_a_card() -> None:
    card = decode_senki("4905040354006")

    assert (card.kind, card.ident, card.stats) == (GameKind.HIDDEN, SOUND_TEST, ())


def test_a_short_code_reads_as_the_thirteen_digits_the_interface_pads_with_zeros() -> None:
    assert fields("99721503") == fields("0000099721503")


def test_an_item_keeps_the_units_of_its_strength_below_ten_where_barcode_world_does_not() -> None:
    senki = decode_senki("0052757569798")
    world = decode_barcode_world("0052757569798")

    assert (senki.traits[4], world.traits[4]) == (14, 24)


def test_a_card_is_made_for_senki_rather_than_for_barcode_world() -> None:
    assert decode_senki("4994699095453").game is Device.SENKI


def test_a_malformed_code_is_refused_before_it_is_read() -> None:
    with pytest.raises(BarcodeError):
        decode_senki("4994699095450")


def test_a_built_fighter_reads_back_as_the_numbers_asked_for() -> None:
    draw = random.Random(1993)  # noqa: S311
    wanted = (draw.randint(1, 199), draw.randint(0, 99), draw.randint(0, 99))
    order = SenkiOrder(
        WARRIOR,
        (
            Constraint.exactly(wanted[0] * 100),
            Constraint.exactly(wanted[1] * 100),
            Constraint.exactly(wanted[2] * 100),
        ),
        ((JOB_KEY, draw.randint(0, 6)),),
    )

    card = build_senki(order)

    assert card is not None
    assert (card.value("WHP"), card.value("WST"), card.value("WDF")) == tuple(
        value * 100 for value in wanted
    )


def test_a_magician_job_asked_of_a_warrior_builds_no_card() -> None:
    assert build_senki(SenkiOrder(WARRIOR, (ANY, ANY, ANY), ((JOB_KEY, 8),))) is None


def test_the_strongest_card_is_a_magician_at_every_ceiling() -> None:
    card = strongest_senki()

    assert (card.value("WHP"), card.value("WST"), card.value("WDF"), card.value("WMP")) == (
        49900,
        19900,
        19900,
        10,
    )
    assert card.traits[0] == MAGICIAN_JOB


def black_store_recorded() -> list[dict[str, object]]:
    return json.loads(BLACK_STORE.read_text("utf-8"))["cards"]


@pytest.mark.parametrize("entry", black_store_recorded(), ids=lambda entry: str(entry["barcode"]))
def test_the_black_store_reads_every_code_as_the_game_did_in_mame(entry: dict[str, object]) -> None:
    stats = black_store_stats(str(entry["barcode"]))

    expected = (entry["hp"], entry["st"], entry["df"]) if entry["black_store"] else None
    assert stats == expected


def test_a_code_read_in_place_reads_the_same_in_the_black_store() -> None:
    assert black_store_stats("0120401154185") is None
