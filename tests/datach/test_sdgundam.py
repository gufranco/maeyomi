"""Tests for reading and building Datach SD Gundam Wars cards."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_reader import printable
from maeyomi.datach.sdgundam import (
    CP_KEY,
    LR_KEY,
    SR_KEY,
    SdGundamOrder,
    build_sdgundam,
    codes_of,
    decode_sdgundam,
    picks_for,
    strongest_sdgundam,
)
from maeyomi.datach.sdgundam_tables import AP_BONUS, BASES, CP_BONUS, DP_BONUS, HP_BONUS
from maeyomi.decoder.errors import BarcodeError
from maeyomi.models.constraint import Constraint

FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "datach_sdgundam.json"
ANY: Constraint = Constraint.anything()


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


def numbers(barcode: str) -> dict[str, int]:
    card = decode_sdgundam(barcode)
    sr, lr, rank = card.traits
    return {
        "ident": card.ident,
        "hp": card.value("GHP"),
        "ap": card.value("AP"),
        "dp": card.value("GDP"),
        "cp": card.value("CP"),
        "rank": rank,
        "sr": sr,
        "lr": lr,
    }


@pytest.mark.parametrize("entry", recorded(), ids=lambda entry: str(entry["barcode"]))
def test_every_code_reads_as_the_game_itself_read_it_in_mame(entry: dict[str, object]) -> None:
    barcode = str(entry["barcode"])

    if entry["kind"] == "command":
        card = decode_sdgundam(barcode)
        assert (card.kind, card.ident) == (GameKind.COMMAND, entry["ident"])
    else:
        expected = {
            key: entry[key] for key in ("ident", "hp", "ap", "dp", "cp", "rank", "sr", "lr")
        }
        assert numbers(barcode) == expected


def test_the_first_card_of_the_box_is_the_gundam_with_its_rifle() -> None:
    assert numbers("0403775140252") == {
        "ident": 0,
        "hp": 3880,
        "ap": 2960,
        "dp": 4360,
        "cp": 9,
        "rank": 4,
        "sr": 0,
        "lr": 4,
    }


def test_a_command_card_carries_no_numbers() -> None:
    card = decode_sdgundam("0465464360068")

    assert (card.kind, card.ident, card.stats) == (GameKind.COMMAND, 118, ())


def test_a_malformed_code_is_refused_before_it_is_read() -> None:
    with pytest.raises(BarcodeError):
        decode_sdgundam("0403775140250")


def test_a_unit_is_built_with_the_numbers_and_weapons_asked_for() -> None:
    hp, ap, dp = BASES[0][0] + HP_BONUS[13], BASES[0][1] + AP_BONUS[6], BASES[0][2] + DP_BONUS[19]
    order = SdGundamOrder(
        0,
        (Constraint.exactly(hp), Constraint.exactly(ap), Constraint.exactly(dp)),
        ((SR_KEY, 1), (LR_KEY, 5), (CP_KEY, 11)),
    )

    card = build_sdgundam(order)

    assert card is not None
    read = numbers(card.barcode)
    assert (read["hp"], read["ap"], read["dp"], read["cp"]) == (hp, ap, dp, 11)
    assert (read["sr"], read["lr"]) == (1, 5)
    assert printable(card.barcode)


def test_a_number_between_two_the_game_holds_takes_the_closest() -> None:
    order = SdGundamOrder(0, (Constraint.exactly(3885), ANY, ANY))

    card = build_sdgundam(order)

    assert card is not None
    assert card.value("GHP") == 3880


def test_a_command_is_built_by_its_number() -> None:
    card = build_sdgundam(SdGundamOrder(118, (ANY, ANY, ANY)))

    assert card is not None
    assert (card.kind, card.ident) == (GameKind.COMMAND, 118)


def test_any_card_is_a_unit_when_none_is_named() -> None:
    card = build_sdgundam(SdGundamOrder(None, (ANY, ANY, ANY)))

    assert card is not None
    assert card.kind is GameKind.UNIT


def test_a_weapon_the_unit_cannot_carry_builds_no_card() -> None:
    assert build_sdgundam(SdGundamOrder(0, (ANY, ANY, ANY), ((SR_KEY, 12),))) is None


def test_a_unit_offers_its_weapons_and_its_cp_values() -> None:
    picks = {pick.key: [option.value for option in pick.options] for pick in picks_for(0)}

    assert picks == {SR_KEY: [0, 1], LR_KEY: [4, 5], CP_KEY: [8, 9, 10, 11]}


def test_a_command_offers_no_choices() -> None:
    assert picks_for(118) == ()


def test_the_strongest_card_is_the_unit_with_the_most_hp_ap_and_dp_at_every_top_bonus() -> None:
    best = max(sum(base[:3]) for base in BASES)
    top = max(HP_BONUS) + max(AP_BONUS) + max(DP_BONUS)

    card = strongest_sdgundam()

    assert card.kind is GameKind.UNIT
    assert card.value("GHP") + card.value("AP") + card.value("GDP") == best + top
    assert card.value("CP") == BASES[card.ident][4] + max(CP_BONUS)


def test_a_unit_the_game_does_not_have_has_no_strongest_card() -> None:
    with pytest.raises(ValueError, match="SD Gundam Wars has no unit 99"):
        strongest_sdgundam(99)


def test_a_command_no_slot_names_builds_no_card() -> None:
    assert build_sdgundam(SdGundamOrder(116, (ANY, ANY, ANY))) is None


def test_a_stream_no_digit_can_build_yields_no_code() -> None:
    assert list(codes_of(1)) == []
