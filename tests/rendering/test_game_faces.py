"""Tests for the faces of cards read by the Datach games after Dragon Ball Z."""

from maeyomi.datach.ultraman import decode_ultraman
from maeyomi.rendering.face import face_of, summary_of
from maeyomi.rendering.labels import Bilingual


def test_a_fighter_prints_its_name_its_kind_and_its_three_numbers() -> None:
    face = face_of(decode_ultraman("0315424322677"))

    assert face.kind == Bilingual("Zoffy", "ゾフィー")
    assert face.detail == Bilingual("Fighter", "せんし")
    assert [(tile.key, tile.value) for tile in face.tiles] == [
        ("PW", 7200),
        ("UST", 6900),
        ("USP", 4800),
    ]


def test_an_item_prints_on_the_item_band_as_an_item_card() -> None:
    face = face_of(decode_ultraman("0416434374356"))

    assert face.kind == Bilingual("Father of Ultra", "ウルトラのちち")
    assert face.detail == Bilingual("Item card", "アイテム カード")


def test_a_summary_names_the_numbers_the_way_the_game_prints_them() -> None:
    summary = summary_of(decode_ultraman("0315424322677"))

    assert summary.stats == Bilingual("PW 7200 / ST 6900 / SP 4800", "PW 7200 / ST 6900 / SP 4800")
    assert summary.kind == "fighter"
