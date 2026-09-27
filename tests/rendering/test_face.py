"""Tests for the target-neutral face a card is drawn from."""

from maeyomi.bb1.decode import decode_first
from maeyomi.bb1.flags import Flag
from maeyomi.decoder.decode import decode
from maeyomi.double.abilities import DoubleAbility
from maeyomi.double.decode import decode_double
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.race import Race
from maeyomi.rendering.ability_icons import (
    AbilityIcon,
    Badge,
    Glyph,
    ability_icon,
    double_icon,
    flag_icon,
)
from maeyomi.rendering.face import face_of
from maeyomi.rendering.icons import RACE_COLOURS, UNKNOWN_KIND_COLOUR
from maeyomi.rendering.labels import (
    ITEM_CARD,
    UNKNOWN_FIGHTER,
    UNKNOWN_KIND,
    Bilingual,
    class_label,
    double_class_label,
    panel_text,
    race_label,
)

CHEAT = "9994699095182"
ARMOUR = "4902102072618"


def test_a_fighter_face_carries_its_race_class_numbers_and_power() -> None:
    character = decode(CHEAT)

    face = face_of(character)

    assert face.band_colour == RACE_COLOURS[Race.MECHANICAL]
    assert face.kind == race_label(Race.MECHANICAL)
    assert face.detail == class_label(character.character_class)
    assert [tile.key for tile in face.tiles] == ["HP", "ST", "DF"]
    assert face.power_code == 18
    assert face.power_text == panel_text(character)
    assert face.power_icon == ability_icon(character.special)


def test_an_item_face_names_itself_an_item_card() -> None:
    face = face_of(decode(ARMOUR))

    assert face.detail == ITEM_CARD
    assert [tile.key for tile in face.tiles] == ["DF"]


def test_a_first_battler_fighter_is_a_warrior_with_its_own_flag_words() -> None:
    face = face_of(decode_first("0120401154185"))

    assert face.kind == race_label(Race.ANIMAL)
    assert face.detail == class_label(CharacterClass.WARRIOR)
    assert face.power_code == 18
    assert face.power_text == Bilingual("Hero", "主人公フラグ(COM/B1モードで主人公として使える)")
    assert face.power_icon == AbilityIcon(Glyph.CROWN)
    assert [(tile.key, tile.value) for tile in face.tiles] == [
        ("HP", 1200),
        ("ST", 400),
        ("DF", 100),
    ]


def test_a_first_battler_helper_item_always_gives_health() -> None:
    face = face_of(decode_first("0000000908092"))

    assert face.detail == ITEM_CARD
    assert [tile.key for tile in face.tiles] == ["HP"]


def test_an_enemy_read_from_the_back_says_its_kind_is_unknown() -> None:
    face = face_of(decode_first("4902102072618"))

    assert face.kind == UNKNOWN_KIND
    assert face.band_colour == UNKNOWN_KIND_COLOUR
    assert face.detail == class_label(CharacterClass.WARRIOR)
    assert [(tile.key, tile.value) for tile in face.tiles] == [
        ("HP", 7200),
        ("ST", 1600),
        ("DF", 100),
    ]


def test_every_first_battler_flag_has_an_icon() -> None:
    icons = [flag_icon(Flag.from_code(code)) for code in range(100)]

    assert icons[5] == AbilityIcon(Glyph.SWORD, Badge.UP)
    assert icons[13] == AbilityIcon(Glyph.SHIELD, Badge.DOWN)
    assert icons[40] == AbilityIcon(Glyph.UNKNOWN)


def test_a_seven_read_card_has_an_unknown_kind_and_the_double_class() -> None:
    face = face_of(decode_double("7821818898978"))

    assert face.kind == UNKNOWN_FIGHTER
    assert face.detail == double_class_label(9)
    assert face.power_text == Bilingual("opponent DF down 80%", "DF80%ダウン")
    assert face.power_icon == AbilityIcon(Glyph.SHIELD, Badge.DOWN)
    assert [(tile.key, tile.value) for tile in face.tiles] == [
        ("HP", 82700),
        ("ST", 18800),
        ("DF", 18900),
    ]


def test_the_double_names_its_priest_and_holy_warrior() -> None:
    assert double_class_label(4) == Bilingual("Priest", "そうりょ")
    assert double_class_label(6) == Bilingual("Holy warrior", "せいせんし")
    assert double_class_label(5) == class_label(CharacterClass.WARRIOR)


def test_a_double_front_read_keeps_its_race_and_reads_its_power_from_the_double_table() -> None:
    face = face_of(decode_double("0451414388503"))

    assert face.kind == race_label(Race.BIRD)
    assert face.power_text == Bilingual(
        "hero in C1 and C2", "C1、C2モードで主人公キャラとして使える"
    )
    assert face.power_icon == AbilityIcon(Glyph.CROWN)


def test_a_double_item_prints_only_what_it_carries() -> None:
    face = face_of(decode_double("4902102072618"))

    assert face.detail == ITEM_CARD
    assert [tile.key for tile in face.tiles] == ["DF"]


def test_every_double_power_has_an_icon() -> None:
    icons = [double_icon(DoubleAbility.from_code(code)) for code in range(100)]

    assert icons[35] == AbilityIcon(Glyph.TARGET, Badge.DOWN)
    assert icons[33] == AbilityIcon(Glyph.UNKNOWN)
    assert icons[90] == AbilityIcon(Glyph.KEY)
