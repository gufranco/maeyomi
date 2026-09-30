"""Tests for serving effect games and Excite Stage '95 through the dispatch table."""

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import DatachGame, GameOrder
from maeyomi.games.excite94 import BEST
from maeyomi.games.excite95 import DRIBBLE, HANDICAP, KICK_SPEED, NO_CARDS
from maeyomi.games.served import (
    BATTLE_RUSH_GAME,
    EXCITE94_GAME,
    EXCITE95_GAME,
    HATAYAMA_GAME,
    VALUE_KEY,
)
from maeyomi.models.constraint import Constraint

ANY = Constraint.anything()


def test_an_excite_item_is_built_with_the_value_picked() -> None:
    card = EXCITE95_GAME.build(GameOrder(KICK_SPEED, (ANY, ANY, ANY), ((VALUE_KEY, 104),)))

    assert card is not None
    assert (card.ident, card.traits) == (KICK_SPEED, (104,))


def test_an_excite_item_without_a_value_is_built_at_its_highest() -> None:
    card = EXCITE95_GAME.build(GameOrder(HANDICAP, (ANY, ANY, ANY)))

    assert card is not None
    assert card.traits == (4,)


def test_an_excite_item_offers_only_the_values_its_kind_carries() -> None:
    options = EXCITE95_GAME.picks(HANDICAP)[0].options

    assert [option.value for option in options] == [1, 2, 3, 4]


def test_an_excite_item_is_described_by_its_ability_and_how_far_it_raises_it() -> None:
    text = EXCITE95_GAME.describe(EXCITE95_GAME.decode("4957368193034"))

    assert text.name == ("Kick speed", "キックスピード")
    assert text.power == (
        "Raises it by 76; in PK mode keeper level +1",
        "76 あがる・PKモードでは キーパーの レベル +1",
    )


def test_an_excite_item_is_found_by_name_or_number() -> None:
    assert EXCITE95_GAME.named("Dribble") == DRIBBLE
    assert EXCITE95_GAME.named(str(NO_CARDS)) == NO_CARDS
    with pytest.raises(ValueError, match=r"unknown J\.League Excite Stage '95 item"):
        EXCITE95_GAME.named("Header")


def test_excite_items_are_drawn_for_random_sheets() -> None:
    assert GameKind.ITEM in EXCITE95_GAME.drawable


def test_a_hatayama_wizard_is_built_with_the_magic_picked() -> None:
    order = GameOrder(1, (ANY, ANY, ANY), (("mp", 42),))

    card = HATAYAMA_GAME.build(order)

    assert card is not None
    assert (card.ident, card.value("WMP")) == (1, 42)


def test_a_hatayama_warrior_offers_no_magic_to_pick() -> None:
    assert HATAYAMA_GAME.picks(0) == ()
    assert [pick.key for pick in HATAYAMA_GAME.picks(1)] == ["mp"]


def test_a_hatayama_battler_names_its_class_and_the_strategy_its_code_picks() -> None:
    text = HATAYAMA_GAME.describe(HATAYAMA_GAME.decode("4912345678010"))

    assert text.power[0] == "Blizzard; graphic 1"


def test_a_code_hatayama_refuses_says_so() -> None:
    text = HATAYAMA_GAME.describe(HATAYAMA_GAME.decode("0000000500005"))

    assert text.name == ("Refused", "よみこまない")


def test_a_hatayama_class_is_found_by_name_or_number() -> None:
    assert HATAYAMA_GAME.named("wizard") == 1
    with pytest.raises(ValueError, match="unknown Hatayama Hatch class"):
        HATAYAMA_GAME.named("Pitcher")


def test_an_excite_94_player_is_described_by_name_and_grades() -> None:
    text = EXCITE94_GAME.describe(EXCITE94_GAME.decode("4900000011005"))

    assert text.name == ("Gamamoto Kunikuni", "がまもと くにくに")
    assert text.power == (
        "KIC A, SHT A, RUN A, DRB A",
        "キック A・シュート A・ラン A・ドリブル A",
    )


def test_an_excite_94_item_is_built_with_the_value_picked() -> None:
    card = EXCITE94_GAME.build(GameOrder(1003, (ANY, ANY, ANY), ((VALUE_KEY, 104),)))

    assert card is not None
    assert card.traits == (104,)


def test_an_excite_94_player_is_found_by_name() -> None:
    assert EXCITE94_GAME.named("がまもと くにくに") == BEST


def test_an_excite_94_player_is_found_by_english_name() -> None:
    assert EXCITE94_GAME.named("gamamoto kunikuni") == BEST


def test_only_an_excite_94_item_offers_a_value() -> None:
    assert EXCITE94_GAME.picks(BEST) == ()
    assert EXCITE94_GAME.picks(1000)[0].key == VALUE_KEY


def test_a_battle_rush_robot_prints_its_weapon_card_beside_its_frame_card() -> None:
    order = GameOrder(3, (ANY, ANY, ANY), (("head", 4), ("attack", 7)))

    frame = BATTLE_RUSH_GAME.build(order)
    weapons = BATTLE_RUSH_GAME.companion(order)

    assert frame is not None
    assert weapons is not None
    assert (frame.ident, weapons.ident, frame.traits[2], weapons.traits[-2]) == (3, 3, 4, 7)


def test_the_strongest_battle_rush_robot_comes_with_its_weapon_card() -> None:
    assert BATTLE_RUSH_GAME.strongest is not None
    frame = BATTLE_RUSH_GAME.strongest()
    weapons = BATTLE_RUSH_GAME.strongest_companion()

    assert weapons is not None
    assert frame.ident == weapons.ident


def test_a_battle_rush_opponent_is_found_by_name_and_described_as_a_frame() -> None:
    ident = BATTLE_RUSH_GAME.named("ミスターX")
    card = BATTLE_RUSH_GAME.build(GameOrder(ident, (ANY, ANY, ANY)))

    assert card is not None
    text = BATTLE_RUSH_GAME.describe(card)
    assert text.detail == ("Frame card: scan it first", "1まいめに よませる")
    assert text.name == ("Misutaa X / Bonbon R-01", "ミスターX / ボンボンR-01")
    assert text.power == (
        "Head 0, body 0, shoulder 0, foot 0, pilot 0",
        "あたま 0・からだ 0・かた 0・あし 0・パイロット 0",
    )


def test_a_battle_rush_opponent_is_found_by_english_name() -> None:
    assert BATTLE_RUSH_GAME.named("bonbon r-01") == BATTLE_RUSH_GAME.named("ミスターX")


def test_a_battle_rush_weapon_card_names_its_levels() -> None:
    order = GameOrder(20, (ANY, ANY, ANY), (("recovery", 1), ("defense", 2)))
    weapons = BATTLE_RUSH_GAME.companion(order)

    assert weapons is not None
    text = BATTLE_RUSH_GAME.describe(weapons)
    assert text.power == (
        "Recovery 1, defense 2, attack 0, speed 0",
        "かいふく 1・ぼうぎょ 2・こうげき 0・スピード 0",
    )


def test_a_shop_barcode_is_described_as_refused_by_battle_rush() -> None:
    text = BATTLE_RUSH_GAME.describe(BATTLE_RUSH_GAME.decode("4912345678904"))

    assert text.name == ("Refused", "よみこまない")


def test_an_unknown_battle_rush_robot_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown Datach Battle Rush robot"):
        BATTLE_RUSH_GAME.named("Gundam")


@pytest.mark.parametrize("game", [EXCITE95_GAME, EXCITE94_GAME])
def test_an_excite_order_naming_no_card_builds_nothing(game: DatachGame) -> None:
    assert game.build(GameOrder(None, (ANY, ANY, ANY))) is None


def test_an_excite_94_item_is_described_by_its_ability_and_how_far_it_raises_it() -> None:
    text = EXCITE94_GAME.describe(EXCITE94_GAME.decode("0000000034111"))

    assert text.name == ("Kick speed", "キックスピード")
    assert text.power == (
        "Raises it by 104; in PK mode saving, level 1",
        "104 あがる・PKモードでは セービング レベル1",
    )


def test_an_unknown_excite_94_card_is_refused() -> None:
    with pytest.raises(ValueError, match=r"unknown J\.League Excite Stage '94 card"):
        EXCITE94_GAME.named("Header")


def test_a_battle_rush_robot_offers_every_part_pilot_weapon_and_level() -> None:
    picks = BATTLE_RUSH_GAME.picks(0)

    assert [(pick.key, len(pick.options)) for pick in picks] == [
        ("head", 32),
        ("body", 32),
        ("shoulder", 32),
        ("foot", 32),
        ("pilot", 16),
        ("weapon", 64),
        ("second_weapon", 64),
        ("recovery", 8),
        ("defense", 8),
        ("attack", 8),
        ("speed", 8),
    ]


def test_a_battle_rush_part_beyond_its_field_builds_no_card() -> None:
    order = GameOrder(3, (ANY, ANY, ANY), (("head", 32),))

    assert (BATTLE_RUSH_GAME.build(order), BATTLE_RUSH_GAME.companion(order)) == (None, None)
