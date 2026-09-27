"""Tests for the target-neutral face a card is drawn from."""

from maeyomi.decoder.decode import decode
from maeyomi.models.race import Race
from maeyomi.rendering.ability_icons import ability_icon
from maeyomi.rendering.face import face_of
from maeyomi.rendering.icons import RACE_COLOURS
from maeyomi.rendering.labels import ITEM_CARD, class_label, panel_text, race_label

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
