"""Tests for a message that says the same thing in English and in Japanese."""

import pytest

from maeyomi.said import Said, field_in_japanese, in_japanese


def test_a_said_message_reads_as_its_english() -> None:
    message = Said(
        "hp of 150 is not a multiple of 100", "たいりょく 150 は 100 の ばいすうでは ない"
    )

    assert (message, str(message)) == ("hp of 150 is not a multiple of 100",) * 2


def test_a_said_message_keeps_its_japanese() -> None:
    message = Said("no card", "カードが ない")

    assert in_japanese(message) == "カードが ない"


def test_a_said_message_survives_being_raised() -> None:
    message = Said("no card", "カードが ない")

    with pytest.raises(ValueError, match="no card") as raised:
        raise ValueError(message)

    assert in_japanese(raised.value.args[0]) == "カードが ない"


def test_a_plain_message_has_no_japanese() -> None:
    assert in_japanese("no card") is None


@pytest.mark.parametrize(
    ("field", "japanese"),
    [("hp", "たいりょく"), ("st", "こうげき"), ("df", "ぼうぎょ"), ("herbs", "やくそう")],
)
def test_a_field_is_named_as_the_page_names_it(field: str, japanese: str) -> None:
    assert field_in_japanese(field) == japanese


def test_an_unlisted_field_keeps_its_name() -> None:
    assert field_in_japanese("pw") == "pw"
