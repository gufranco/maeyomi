"""Tests for the table of Datach games every surface dispatches through."""

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.games import GAMES, GameOrder, game_for
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

ANY: Constraint = Constraint.anything()


def test_every_game_after_dragon_ball_z_has_an_entry() -> None:
    assert set(GAMES) == {device for device in Device if device.is_game} - {Device.DATACH_DBZ}


def test_a_machine_or_dragon_ball_z_has_no_entry() -> None:
    assert game_for(Device.BB2) is None
    assert game_for(Device.DATACH_DBZ) is None


def test_each_game_reads_what_it_builds() -> None:
    for device, game in GAMES.items():
        card = game.build(GameOrder(game.entries()[0].ident, (ANY, ANY, ANY)))

        assert card is not None, device
        assert game.decode(card.barcode) == card


def test_each_game_lists_its_cards_with_names_in_both_languages() -> None:
    for game in GAMES.values():
        entries = game.entries()

        assert entries
        assert all(entry.english and entry.japanese for entry in entries)


def test_each_game_describes_a_card_it_read() -> None:
    game = GAMES[Device.DATACH_ULTRAMAN]

    text = game.describe(game.decode("0315424322677"))

    assert text.name == ("Zoffy", "ゾフィー")
    assert text.detail == ("Fighter", "せんし")


def test_an_item_is_described_as_an_item() -> None:
    game = GAMES[Device.DATACH_ULTRAMAN]

    text = game.describe(game.decode("0416434374356"))

    assert text.detail == ("Item card", "アイテム カード")


def test_the_strongest_card_is_one_the_game_reads_back() -> None:
    game = GAMES[Device.DATACH_ULTRAMAN]

    assert game.strongest is not None
    card = game.strongest()

    assert game.decode(card.barcode) == card


@pytest.mark.parametrize(("typed", "expected"), [("Zoffy", 3), ("ゼットン", 8)])
def test_a_card_is_found_by_the_name_the_game_gives_it(typed: str, expected: int) -> None:
    assert GAMES[Device.DATACH_ULTRAMAN].named(typed) == expected


def test_a_kind_that_is_not_an_item_is_a_fighter_in_ultraman_club() -> None:
    kinds = {entry.kind for entry in GAMES[Device.DATACH_ULTRAMAN].entries()}

    assert kinds == {GameKind.FIGHTER, GameKind.ITEM}


def test_an_sd_gundam_unit_is_described_by_its_model_and_weapons() -> None:
    game = GAMES[Device.DATACH_SD_GUNDAM]

    text = game.describe(game.decode("0403775140252"))

    assert text.name == ("Gundam", "ガンダム")
    assert text.detail == ("RX-78", "RX-78")
    assert text.power == ("SR Beam saber, LR Beam rifle", "SR ビームサーベル  LR ビームライフル")


def test_an_sd_gundam_command_is_described_by_its_effect_and_cost() -> None:
    game = GAMES[Device.DATACH_SD_GUNDAM]

    text = game.describe(game.decode("0465464360068"))

    assert text.detail == ("Command card", "コマンド カード")
    assert text.power[0].endswith("Costs 7 CP.")


def test_a_game_without_choices_offers_none() -> None:
    assert GAMES[Device.DATACH_ULTRAMAN].picks(3) == ()


def test_a_yu_yu_hakusho_item_that_adds_numbers_says_how_much() -> None:
    game = GAMES[Device.DATACH_YUYU]

    text = game.describe(game.decode("0967652615603"))

    assert text.power == ("Adds 500 HP.", "このカードは、HPが 500 アップするぞ。")


def test_a_yu_yu_hakusho_rule_item_says_what_it_changes() -> None:
    game = GAMES[Device.DATACH_YUYU]

    text = game.describe(game.decode("0946730251315"))

    assert text.power[0] == "Halves the time limit of versus mode."


def test_a_yu_yu_hakusho_fighter_without_techniques_says_so() -> None:
    game = GAMES[Device.DATACH_YUYU]
    card = game.build(GameOrder(1, (ANY, ANY, ANY), (("moves", 4),)))

    assert card is not None
    assert game.describe(card).power == ("No technique", "わざ なし")


def test_the_hidden_toguro_is_described_as_hidden() -> None:
    game = GAMES[Device.DATACH_YUYU]

    assert game.strongest is not None
    assert game.describe(game.strongest()).detail == ("Hidden fighter", "かくし キャラクター")


def test_a_j_league_team_card_is_described_by_its_club() -> None:
    game = GAMES[Device.DATACH_JLEAGUE]

    text = game.describe(game.decode("1300400200000"))

    assert text.detail == ("Team card", "チーム カード")
    assert text.power == ("Kashima Antlers", "鹿島アントラーズ")


def test_a_j_league_game_has_no_strongest_card() -> None:
    assert GAMES[Device.DATACH_JLEAGUE].strongest is None


def test_a_barcode_world_item_is_described_by_its_kind_and_number() -> None:
    game = GAMES[Device.BARCODE_WORLD]

    text = game.describe(game.decode("0021909500408"))

    assert text.name == ("Weapon, one use", "ぶき (1かい)")
    assert text.power[0] == "No. 2 in the game's list"


def test_a_barcode_world_fighter_is_described_by_class_job_and_ability() -> None:
    game = GAMES[Device.BARCODE_WORLD]

    text = game.describe(game.decode("0315424322677"))

    assert text.name == ("Warrior", "せんし")
    assert text.detail == ("Job 2, speed 2", "しょくぎょう 2・すばやさ 2")


@pytest.mark.parametrize(("typed", "expected"), [("Magician", 1), ("せんし", 0), ("1", 1)])
def test_a_barcode_world_class_is_found_by_name_or_number(typed: str, expected: int) -> None:
    assert GAMES[Device.BARCODE_WORLD].named(typed) == expected


def test_an_unknown_barcode_world_class_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown Barcode World fighter"):
        GAMES[Device.BARCODE_WORLD].named("Ninja")


def test_only_the_datach_games_use_the_datach_reader() -> None:
    assert not GAMES[Device.BARCODE_WORLD].datach_reader
    assert GAMES[Device.DATACH_ULTRAMAN].datach_reader
