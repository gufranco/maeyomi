"""Tests for the web interface payload shapes."""

import pytest
from pydantic import ValidationError

from barcode_battler.decoder.decode import decode
from barcode_battler.models.race import Race
from barcode_battler.models.special_ability import SpecialAbility
from barcode_battler.ui.schemas import AbilityView, CardSpec, CharacterView, RaceView, RandomSpec


def test_a_card_spec_defaults_to_no_constraints() -> None:
    spec = CardSpec()

    assert spec.hp is None
    assert spec.race is None
    assert spec.name == "Card"


def test_the_class_field_is_accepted_under_its_printed_name() -> None:
    spec = CardSpec.model_validate({"class": "warrior"})

    assert spec.character_class == "warrior"


@pytest.mark.parametrize(("field", "value"), [("job", 10), ("speed", -1), ("ability", 100)])
def test_an_out_of_range_digit_is_rejected(field: str, value: int) -> None:
    with pytest.raises(ValidationError):
        CardSpec.model_validate({field: value})


def test_a_random_spec_bounds_the_batch_size() -> None:
    with pytest.raises(ValidationError):
        RandomSpec.model_validate({"count": 0})


def test_a_character_view_carries_every_decoded_field() -> None:
    view = CharacterView.of(decode("0401207237501"))

    assert view.hp == 4000
    assert view.race == "aquatic"
    assert view.character_class == "warrior"
    assert view.special.code == 50
    assert view.read_type == "front"


def test_an_item_view_has_no_class_and_no_speed() -> None:
    view = CharacterView.of(decode("0000600602017"))

    assert view.character_class is None
    assert view.speed is None


def test_every_race_is_served_in_both_languages() -> None:

    for race in Race:
        view = RaceView.of(race)
        assert view.label
        assert view.label_ja
        assert view.description_ja
        assert not view.description_ja.isascii()


def test_every_ability_is_served_in_both_languages() -> None:

    view = AbilityView.of(SpecialAbility.from_code(18))

    assert view.description == "own attack doubled"
    assert view.description_ja == "自分の破壊力１００％アップ 2倍剣"
