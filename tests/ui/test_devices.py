"""Tests for the web page's device switch: every device and game, one set of routes."""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from maeyomi.barcode.geometry import PRINT_DPI
from maeyomi.barcode.verify import decode_image, decode_pdf
from maeyomi.bb1.decode import decode_first
from maeyomi.datach.dbz import decode_dbz
from maeyomi.double.decode import decode_double
from maeyomi.models.device import Device
from maeyomi.registry import printable_as
from maeyomi.rendering.preview import card_png
from maeyomi.ui.app import create_app
from maeyomi.ui.devices import FORMS, facts_of

GOKU = "0022248300117"
KORIN = "0120631203219"


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(create_app(), base_url="http://localhost")


def test_every_device_is_offered_with_its_form(client: TestClient) -> None:
    body = client.get("/api/devices").json()

    assert [entry["key"] for entry in body] == [device.value for device in Device]
    dbz = next(entry for entry in body if entry["key"] == "dbz")
    assert dbz["fields"] == ["dbz", "stats", "nearest"]
    assert (dbz["hp_max"], dbz["steps"]) == (99500, [500, 250, 250])
    assert dbz["stat_keys"] == ["stat.hp", "stat.bp", "stat.dp"]
    assert dbz["sheet_fields"] == ["third"]
    assert dbz["group"] == "game"
    machines = {"bb2", "bb1", "double"}
    assert {entry["group"] for entry in body if entry["key"] in machines} == {"machine"}
    assert {entry["group"] for entry in body if entry["key"] not in machines} == {"game"}
    assert dbz["ranges"] == [[10000, 60000], [5000, 30000], [5000, 30000]]


def test_every_game_is_filed_under_the_platform_it_runs_on(client: TestClient) -> None:
    body = client.get("/api/devices").json()

    platforms = {entry["key"]: entry["platform"] for entry in body}

    assert {platforms[key] for key in ("bb2", "bb1", "double")} == {"machine"}
    assert {platforms[key] for key in ("dbz", "battlerush", "jleague")} == {"datach"}
    assert platforms["barcodeworld"] == "famicom"
    assert {platforms[key] for key in ("senki", "lupin", "excite94", "hatayama")} == {
        "super_famicom"
    }


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


def test_a_battle_rush_preview_keeps_the_check_digit_the_game_marks(client: TestClient) -> None:
    response = client.post(
        "/api/preview", json={"barcode": "0000000000009", "device": "battlerush"}
    )

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


def test_a_random_sheet_is_drawn_for_the_chosen_device(
    client: TestClient, tmp_path: object
) -> None:
    payload = {
        "device": "dbz",
        "count": 3,
        "seed": 4,
        "hp": "10000-60000",
        "st": "5000-30000",
        "df": "5000-30000",
    }

    response = client.post("/api/random", json=payload)
    path = f"{tmp_path}/random.pdf"
    with open(path, "wb") as handle:  # noqa: PTH123
        handle.write(response.content)

    codes = decode_pdf(path)
    assert len(codes) == 3
    assert all(10000 <= decode_dbz(code).hp <= 60000 for code in codes)


def test_a_random_preview_counts_the_chosen_device(client: TestClient) -> None:
    payload = {"device": "bb1", "count": 2, "seed": 4, "hp": "1000-9000"}

    body = client.post("/api/sheet-preview", json=payload).json()

    assert body["count"] == 2


def test_a_random_sheet_names_a_field_the_game_cannot_read(client: TestClient) -> None:
    response = client.post("/api/sheet-preview", json={"device": "dbz", "race": "human"})

    assert response.status_code == 422
    assert response.json()["detail"] == "Datach Dragon Ball Z does not read race"


def test_the_back_read_ranges_are_offered_where_a_device_reads_backwards(
    client: TestClient,
) -> None:
    body = {entry["key"]: entry for entry in client.get("/api/devices").json()}

    assert body["bb2"]["back_ranges"] == [[0, 49900], [2000, 11900], [0, 9900]]
    assert body["bb1"]["back_ranges"] == [[100, 10000], [1000, 1900], [100, 900]]
    assert body["double"]["back_ranges"] is None
    assert body["dbz"]["back_ranges"] is None


def test_ultraman_club_offers_its_type_picker_and_numbers_up_to_9900(client: TestClient) -> None:
    body = client.get("/api/devices").json()

    ultraman = next(entry for entry in body if entry["key"] == "ultraman")

    assert ultraman["fields"] == ["game", "stats"]
    assert (ultraman["hp_max"], ultraman["steps"]) == (9900, [100, 100, 100])
    assert ultraman["stat_keys"] == ["stat.pw", "stat.ust", "stat.usp"]


def test_a_game_lists_every_card_it_reads_for_its_picker(client: TestClient) -> None:
    body = client.get("/api/game-cards/ultraman").json()

    assert len(body) == 51
    assert body[3] == {"id": 3, "kind": "fighter", "english": "Zoffy", "japanese": "ゾフィー"}


def test_a_machine_lists_no_game_cards(client: TestClient) -> None:
    assert client.get("/api/game-cards/bb2").json() == []


def test_an_ultraman_club_card_is_built_with_the_numbers_asked_for(client: TestClient) -> None:
    payload = {"device": "ultraman", "character": "Zoffy", "hp": "7200", "st": "6900", "df": "4800"}

    body = client.post("/api/device-card", json=payload).json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert facts["PW"] == "7200"
    assert facts["ST"] == "6900"
    assert facts["SP"] == "4800"
    assert facts["Kind"] == "Zoffy"


def test_ultraman_club_refuses_a_number_it_cannot_hold(client: TestClient) -> None:
    payload = {"device": "ultraman", "hp": "7250", "st": "100", "df": "100"}

    response = client.post("/api/device-card", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == [
        "Datach Ultraman Club reads no card like the one asked for"
    ]


def test_ultraman_club_refuses_a_type_it_does_not_have(client: TestClient) -> None:
    payload = {"device": "ultraman", "character": "Godzilla", "hp": "100", "st": "100", "df": "100"}

    response = client.post("/api/device-card", json=payload)

    assert response.status_code == 422
    assert "unknown Ultraman Club type" in response.json()["detail"][0]


def test_ultraman_club_refuses_a_field_it_does_not_read(client: TestClient) -> None:
    payload = {"device": "ultraman", "race": "mechanical", "hp": "100", "st": "100", "df": "100"}

    response = client.post("/api/device-card", json=payload)

    assert response.json()["detail"] == ["Datach Ultraman Club does not read race"]


def test_ultraman_club_has_a_cheat_card_at_the_top_of_all_three(client: TestClient) -> None:
    body = client.post("/api/device-cheat", json={"device": "ultraman"}).json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert (facts["PW"], facts["ST"], facts["SP"]) == ("9900", "9900", "9900")


def test_an_sd_gundam_unit_offers_its_weapons_and_cp(client: TestClient) -> None:
    body = client.get("/api/game-picks/sdgundam/0").json()

    assert [pick["key"] for pick in body] == ["sr", "lr", "cp"]
    assert body[0]["options"][1] == {"value": 1, "english": "Vulcan", "japanese": "バルカン"}


def test_an_sd_gundam_card_is_built_with_its_picks(client: TestClient) -> None:
    payload = {"device": "sdgundam", "character": "0", "picks": {"sr": 1, "lr": 5}}

    body = client.post("/api/device-card", json=payload).json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert facts["Weapons"] == "SR Vulcan, LR Bazooka"


def test_a_number_between_two_the_game_holds_is_marked_as_the_closest(client: TestClient) -> None:
    payload = {"device": "sdgundam", "character": "0", "hp": "3885"}

    body = client.post("/api/device-card", json=payload).json()

    assert body["is_exact"] is False


def test_a_monster_maker_hero_is_built_exactly_with_its_later_reading(
    client: TestClient,
) -> None:
    payload = {
        "device": "monstmkb",
        "character": "17",
        "hp": "5000",
        "st": "1800",
        "df": "1200",
        "picks": {"later": 1705},
    }

    body = client.post("/api/device-card", json=payload).json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert body["is_exact"] is True
    assert facts["Later in the game"].startswith("Lorian, level 5:")


def test_a_machine_offers_no_game_picks(client: TestClient) -> None:
    assert client.get("/api/game-picks/bb2/0").json() == []


def test_yu_yu_hakusho_offers_its_card_and_choices_but_no_sliders(client: TestClient) -> None:
    body = client.get("/api/devices").json()

    yuyu = next(entry for entry in body if entry["key"] == "yuyu")

    assert yuyu["fields"] == ["game", "picks"]
    assert yuyu["sheet_fields"] == []


def test_a_yu_yu_hakusho_fighter_is_built_with_the_techniques_picked(client: TestClient) -> None:
    payload = {"device": "yuyu", "character": "Yusuke", "picks": {"moves": 9}}

    body = client.post("/api/device-card", json=payload).json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert facts["Techniques"] == "Spirit Gun, Headbutt"
    assert (facts["HP"], facts["SP"]) == ("3000", "2000")
    assert body["is_exact"] is True


def test_a_j_league_card_is_built_for_the_player_asked_for(client: TestClient) -> None:
    payload = {"device": "jleague", "character": "Zico"}

    body = client.post("/api/device-card", json=payload).json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert facts["Kind"] == "Zico"
    assert facts["Player"] == "No. 10 of Kashima Antlers"


def test_the_j_league_cheat_is_refused_with_its_reason(client: TestClient) -> None:
    response = client.post("/api/device-cheat", json={"device": "jleague"})

    assert response.status_code == 422
    assert "carry no numbers" in response.json()["detail"]


def test_a_barcode_world_magician_offers_only_magician_jobs(client: TestClient) -> None:
    body = client.get("/api/game-picks/barcodeworld/1").json()

    assert [option["value"] for option in body[0]["options"]] == [7, 8, 9]
    assert [pick["key"] for pick in body] == ["job", "speed", "ability"]


def test_a_barcode_world_card_is_built_with_its_numbers(client: TestClient) -> None:
    payload = {"device": "barcodeworld", "character": "0", "hp": "5000", "st": "1200", "df": "3400"}

    body = client.post("/api/device-card", json=payload).json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert (facts["HP"], facts["ST"], facts["DF"], facts["PP"]) == ("5000", "1200", "3400", "5")


def test_a_senki_card_is_built_with_its_numbers_and_read_as_senki(client: TestClient) -> None:
    payload = {"device": "senki", "character": "1", "hp": "35900", "st": "15000", "df": "9900"}

    body = client.post("/api/device-card", json=payload).json()

    facts = {fact["label"]: fact["value"] for fact in body["facts"]}
    assert (facts["HP"], facts["ST"], facts["DF"], facts["MP"]) == ("35900", "15000", "9900", "10")


def test_senki_has_no_set_of_real_cards_to_offer(client: TestClient) -> None:
    body = client.get("/api/official?device=senki").json()

    assert (body["sets"], body["total"]) == ([], 0)


def test_a_battle_rush_robot_comes_back_with_its_weapon_card(client: TestClient) -> None:
    payload = {"device": "battlerush", "character": "5", "picks": {"attack": 7}}

    body = client.post("/api/device-card", json=payload).json()

    assert body["companion"] is not None
    assert body["companion"] != body["barcode"]


def test_the_battle_rush_cheat_comes_back_with_its_weapon_card(client: TestClient) -> None:
    body = client.post("/api/device-cheat", json={"device": "battlerush"}).json()

    assert body["companion"] is not None


def test_a_single_card_game_brings_no_companion(client: TestClient) -> None:
    body = client.post("/api/device-cheat", json={"device": "lupin"}).json()

    assert body["companion"] is None


def test_every_device_lists_its_cheat_kinds(client: TestClient) -> None:
    body = client.get("/api/devices").json()

    kinds = {entry["key"]: [kind["key"] for kind in entry["cheat_kinds"]] for entry in body}
    assert kinds["bb2"] == ["fighter", "warrior", "items"]
    assert kinds["jleague"] == []


def test_a_cheat_kind_returns_every_card_it_prints(client: TestClient) -> None:
    response = client.post("/api/device-cheat", json={"device": "bb2", "kind": "items"})

    body = response.json()
    assert response.status_code == 200
    assert len(body["cards"]) == 5
    assert body["barcode"] == body["cards"][0]


def test_a_cheat_kind_the_device_lacks_is_refused_in_both_languages(client: TestClient) -> None:
    response = client.post("/api/device-cheat", json={"device": "bb2", "kind": "ninja"})

    assert response.status_code == 422
    assert "its kinds are" in response.json()["detail"]
    assert "えらべるのは" in response.json()["detail_ja"]


def test_every_cheat_kind_is_previewed_together(client: TestClient) -> None:
    response = client.post("/api/cheat-preview", json={"device": "bb2", "kind": "all"})

    body = response.json()
    assert response.status_code == 200
    assert body["count"] == 7
    assert body["pages"][0].startswith("data:image/png;base64,")


def test_one_cheat_card_is_previewed_alone(client: TestClient) -> None:
    response = client.post("/api/cheat-preview", json={"device": "bardigun", "kind": "power"})

    body = response.json()
    assert (body["count"], body["single"], len(body["pages"])) == (1, True, 1)


def test_one_cheat_kind_with_no_name_is_named_after_itself(
    client: TestClient,
) -> None:
    response = client.post("/api/device-cheat", json={"device": "bardigun", "kind": "power"})

    assert response.json()["name"] == "Most power"


def test_a_name_typed_for_every_kind_at_once_is_refused(client: TestClient) -> None:
    response = client.post(
        "/api/cheat-preview", json={"device": "bardigun", "kind": "all", "name": "Rex"}
    )

    assert response.status_code == 422
    assert "one kind" in response.json()["detail"]


def test_every_cheat_kind_prints_on_one_sheet(client: TestClient) -> None:
    response = client.post("/api/cheat-sheet", json={"device": "bb2", "kind": "all"})

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_a_game_with_no_cheat_previews_nothing(client: TestClient) -> None:
    response = client.post("/api/cheat-preview", json={"device": "jleague", "kind": "all"})

    assert response.status_code == 422
    assert "carry no numbers" in response.json()["detail"]


def test_a_code39_card_is_read_on_its_own_device(client: TestClient) -> None:
    response = client.get("/api/read/cardasobu/AA082KRC00V01")

    body = response.json()
    assert body["barcode"] == "AA082KRC00V01"
    assert any(fact["value"] == "Whale" for fact in body["facts"])


def test_a_code39_text_with_a_slash_is_refused_rather_than_lost(client: TestClient) -> None:
    response = client.get("/api/read/cardasobu/AA/01")

    assert response.status_code == 400
    assert "no Card de Asobu card" in response.json()["detail"]


def test_a_code39_card_previews_as_a_card(client: TestClient) -> None:
    response = client.post(
        "/api/preview", json={"barcode": "AA082KRC00V01", "name": "くじら", "device": "cardasobu"}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_a_code39_card_prints_a_symbol_that_scans() -> None:
    card = printable_as(Device.CARD_DE_ASOBU, "AA082KRC00V01", "くじら")

    image = Image.open(io.BytesIO(card_png(card, dpi=PRINT_DPI))).convert("RGB")

    assert decode_image(image) == ["AA082KRC00V01"]


def test_every_device_says_which_symbology_its_reader_takes(client: TestClient) -> None:
    views = {view["key"]: view["symbology"] for view in client.get("/api/devices").json()}

    assert (views["cardasobu"], views["bb2"]) == ("code39", "ean")


def test_every_device_names_the_reader_its_page_text_describes(client: TestClient) -> None:
    views = {view["key"]: view["reader"] for view in client.get("/api/devices").json()}

    assert (views["bb2"], views["densha"], views["ochaken"]) == ("ean", "stripes", "ochaken")


def test_a_stripe_reader_says_how_many_places_its_cards_carry(client: TestClient) -> None:
    views = {view["key"]: view["places"] for view in client.get("/api/devices").json()}

    assert (views["bb2"], views["densha"], views["ochaken"]) == (0, 12, 16)


def test_a_stripe_card_is_read_by_the_number_printed_on_it(client: TestClient) -> None:
    response = client.get("/api/read/ochaken/13")

    body = response.json()
    assert (response.status_code, body["barcode"], body["name"]) == (
        200,
        "0100100011000101",
        "のみ薬",
    )


def test_a_card_only_reader_names_the_card_it_read(client: TestClient) -> None:
    names = [
        client.get(f"/api/read/{device}/{code}").json()["name"]
        for device, code in (("densha", "100010110011"), ("bb2", "4901085061169"))
    ]

    assert names == ["E1系 Maxたにがわ", ""]


def test_a_built_in_game_is_listed_among_the_machines(client: TestClient) -> None:
    views = {view["key"]: view["platform"] for view in client.get("/api/devices").json()}

    assert (views["ochaken"], views["densha"]) == ("machine", "beena")


def test_every_device_says_whether_a_sheet_holds_to_number_ranges(client: TestClient) -> None:
    views = {view["key"]: view["ranged"] for view in client.get("/api/devices").json()}

    assert (views["bb2"], views["dbz"], views["monstmkb"]) == (True, True, True)
    assert (views["wantame"], views["jleague"], views["battlerush"]) == (False, False, False)


def test_a_ds_game_draws_a_sheet_from_its_own_cards(client: TestClient) -> None:
    response = client.post("/api/sheet-preview", json={"count": 9, "seed": 4, "device": "wantame"})

    assert response.status_code == 200
    assert response.json()["count"] == 9
