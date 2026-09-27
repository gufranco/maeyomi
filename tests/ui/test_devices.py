"""Tests for the web page's device switch: every device and game, one set of routes."""

import pytest
from fastapi.testclient import TestClient

from maeyomi.barcode.verify import decode_pdf
from maeyomi.bb1.decode import decode_first
from maeyomi.datach.dbz import decode_dbz
from maeyomi.double.decode import decode_double
from maeyomi.models.device import Device
from maeyomi.ui.app import create_app
from maeyomi.ui.devices import FORMS, facts_of

GOKU = "0022248300117"
KORIN = "0120631203219"


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(create_app())


def test_every_device_is_offered_with_its_form(client: TestClient) -> None:
    body = client.get("/api/devices").json()

    assert [entry["key"] for entry in body] == [device.value for device in Device]
    dbz = next(entry for entry in body if entry["key"] == "dbz")
    assert dbz["fields"] == ["dbz", "nearest"]
    assert (dbz["hp_max"], dbz["steps"]) == (99500, [500, 250, 250])
    assert dbz["stat_keys"] == ["stat.hp", "stat.bp", "stat.dp"]


def test_every_device_has_a_form() -> None:
    assert set(FORMS) == set(Device)


def test_the_dragon_ball_choices_name_every_fighter_and_item(client: TestClient) -> None:
    body = client.get("/api/dbz-characters").json()

    goku = next(entry for entry in body if entry["id"] == 0)
    senzu = next(entry for entry in body if entry["id"] == 33)
    assert (goku["kind"], goku["english"], goku["japanese"]) == ("fighter", "Goku", "ゴクウ")
    assert (senzu["kind"], senzu["english"]) == ("item", "Senzu bean")


def test_a_barcode_is_read_the_way_the_chosen_device_reads_it(client: TestClient) -> None:
    body = client.get(f"/api/read/dbz/{GOKU}").json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert body["barcode"] == GOKU
    assert facts["Kind"] == "Goku"
    assert facts["HP"] == "49500"
    assert facts["BP"] == "28250"
    assert facts["Special moves"] == "Special move level 1"


def test_a_dragon_ball_item_is_read_with_its_effect(client: TestClient) -> None:
    body = client.get(f"/api/read/dbz/{KORIN}").json()

    facts = {fact["label"]: fact["value_ja"] for fact in body["facts"]}
    assert facts["Kind"] == "カリンさま"
    assert facts["Effect"] == "HP BP DPに 6000P プラス"


def test_an_unknown_device_is_refused(client: TestClient) -> None:
    response = client.get(f"/api/read/gameboy/{GOKU}")

    assert response.status_code == 422
    assert "unknown device 'gameboy'" in response.json()["detail"]


def test_a_code_the_device_refuses_is_a_bad_request(client: TestClient) -> None:
    assert client.get("/api/read/dbz/0022248300118").status_code == 400


def test_a_dragon_ball_card_is_built_to_order(client: TestClient) -> None:
    response = client.post(
        "/api/device-card",
        json={"device": "dbz", "character": "vegeta", "level": 2, "hp": "40000"},
    )

    assert response.status_code == 200
    card = decode_dbz(response.json()["barcode"])
    assert (card.character, card.level, card.hp) == (7, 2, 40000)


def test_a_dragon_ball_card_falls_back_to_the_nearest_when_asked(client: TestClient) -> None:
    payload = {"device": "dbz", "character": "7", "level": 2, "hp": "40000", "st": "20000"}

    exact = client.post("/api/device-card", json={**payload, "df": "15000"})
    near = client.post("/api/device-card", json={**payload, "df": "15000", "nearest": True})

    assert exact.status_code == 422
    assert near.status_code == 200
    assert near.json()["is_exact"] is False
    assert decode_dbz(near.json()["barcode"]).character == 7


def test_the_first_barcode_battler_builds_to_order(client: TestClient) -> None:
    response = client.post("/api/device-card", json={"device": "bb1", "hp": "9000"})

    assert response.status_code == 200
    assert decode_first(response.json()["barcode"]).hp == 9000


def test_the_double_builds_to_order(client: TestClient) -> None:
    response = client.post("/api/device-card", json={"device": "double", "hp": "9000"})

    assert response.status_code == 200
    assert decode_double(response.json()["barcode"]).hp == 9000


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        ({"device": "dbz", "race": "human"}, "Datach Dragon Ball Z does not read race"),
        ({"device": "dbz", "character": "Mr. Satan"}, "unknown character 'Mr. Satan'"),
        ({"device": "dbz", "hp": "99600"}, "hp of 99600 is above 99500"),
        ({"device": "double", "backRead": True}, "--device bb2"),
        ({"device": "bb1", "hp": "abc"}, "cannot read 'abc'"),
    ],
    ids=["unread", "unknown-name", "ceiling", "double-back-read", "unparsable"],
)
def test_an_impossible_device_card_names_the_reason(
    client: TestClient, payload: dict[str, object], reason: str
) -> None:
    response = client.post("/api/device-card", json=payload)

    assert response.status_code == 422
    assert reason in str(response.json()["detail"])


@pytest.mark.parametrize(
    ("device", "expected"),
    [("bb1", ("HP", "19900")), ("double", ("ST", "99900")), ("dbz", ("HP", "99500"))],
)
def test_the_cheat_is_the_strongest_card_of_the_chosen_device(
    client: TestClient, device: str, expected: tuple[str, str]
) -> None:
    body = client.post("/api/device-cheat", json={"device": device, "name": "Grandma"}).json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert body["name"] == "Grandma"
    assert facts[expected[0]] == expected[1]


def test_the_cheat_keeps_its_own_name_when_none_is_typed(client: TestClient) -> None:
    body = client.post("/api/device-cheat", json={"device": "dbz"}).json()

    assert body["name"] == "Maximus Cheatimus"


def test_a_preview_is_drawn_with_the_chosen_device(client: TestClient) -> None:
    response = client.post("/api/preview", json={"barcode": GOKU, "name": "G", "device": "dbz"})

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_a_sheet_prints_cards_for_the_chosen_device(client: TestClient, tmp_path: object) -> None:
    response = client.post(
        "/api/barcode-sheet", json={"cards": [{"barcode": GOKU, "name": "G", "device": "dbz"}]}
    )
    path = f"{tmp_path}/sheet.pdf"
    with open(path, "wb") as handle:  # noqa: PTH123
        handle.write(response.content)

    assert decode_pdf(path) == [GOKU]


def test_the_facts_of_a_card_come_from_the_face_it_prints() -> None:
    facts = facts_of(decode_first("0120401154185"))

    assert [fact.label for fact in facts][:2] == ["Kind", "Type"]
    assert facts[-1].label.startswith("Special power")


@pytest.mark.parametrize(
    ("device", "barcode", "fact"),
    [
        ("double", "7821818898978", ("ST", "18800")),
        ("bb2", "9994699095182", ("HP", "99900")),
        ("bb1", "0120401154185", ("HP", "1200")),
    ],
)
def test_every_device_reads_through_the_same_route(
    client: TestClient, device: str, barcode: str, fact: tuple[str, str]
) -> None:
    body = client.get(f"/api/read/{device}/{barcode}").json()

    facts = {entry["label"]: entry["value"] for entry in body["facts"]}
    assert facts[fact[0]] == fact[1]


def test_the_second_barcode_battler_cheat_is_reachable_through_the_same_route(
    client: TestClient,
) -> None:
    body = client.post("/api/device-cheat", json={"device": "bb2"}).json()

    facts = {entry["label"]: entry["value"] for entry in body["facts"]}
    assert facts["HP"] == "99900"
