"""Tests for the target-neutral face a card is drawn from."""

from maeyomi.bb1.decode import decode_first
from maeyomi.bb1.flags import Flag
from maeyomi.decoder.decode import decode
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.race import Race
from maeyomi.rendering.ability_icons import AbilityIcon, Badge, Glyph, ability_icon, flag_icon
from maeyomi.rendering.face import face_of
from maeyomi.rendering.icons import RACE_COLOURS, UNKNOWN_KIND_COLOUR
from maeyomi.rendering.labels import (
    ITEM_CARD,
    UNKNOWN_KIND,
    Bilingual,
    class_label,
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
