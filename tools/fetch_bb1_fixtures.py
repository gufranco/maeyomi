import json
import re
import sys
import urllib.parse
from datetime import UTC, datetime

from fetch_fixtures import BASE, get, lead, num, text

PAGES = (
    "バーコードバトラー カードリスト",
    "チューハイカーンの逆襲 カードリスト",
    "最後の決戦ゴッドＶＳマザー カードリスト",
    "バーコードバトラーキャンデー カードリスト",
)
TABLE = re.compile(r"(<table.*?</table>)", re.S)
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
KEYS = {
    "HP": "hp",
    "ST": "st",
    "DF": "df",
    "DX": "dx",
    "種族・種別": "race",
    "職業・種類": "job",
    "特殊能力": "special",
}


def codes(doc):
    found = {}
    for row in ROW.findall(doc):
        cells = [text(c) for c in CELL.findall(row)]
        at = next((i for i, c in enumerate(cells) if re.fullmatch(r"\d{8}|\d{13}", c)), None)
        if at is None or at < 1:
            continue
        type_no = cells[at - 2] if at >= 3 else ""
        found.setdefault(cells[at - 1], (type_no, cells[at]))
    return found


def names_before(preceding, known):
    names = []
    for chunk in preceding.split("/"):
        hits = [n for n in known if chunk.strip().endswith(n)]
        if hits:
            names.append(max(hits, key=len))
    return names


def detail_rows(part):
    rows = [[text(c) for c in CELL.findall(r)] for r in ROW.findall(part)]
    if not rows or rows[0][:3] != ["HP", "ST", "DF"]:
        return []
    return [dict(zip(rows[0], r)) for r in rows[1:]]


def entry(page, url, name, type_no, code, values):
    fields = {KEYS[k]: v for k, v in values.items() if k in KEYS}
    return {
        "barcode": code,
        "name": name,
        "type_no": type_no,
        "source_page": page,
        "source_url": url,
        "hp": num(fields.get("hp", "")),
        "st": num(fields.get("st", "")),
        "df": num(fields.get("df", "")),
        "dx": num(fields.get("dx", "")),
        "race": lead(fields.get("race", "")),
        "job": lead(fields.get("job", "")),
        "special": lead(fields.get("special", "")),
    }


def parse(page, url, doc):
    known = codes(doc)
    parts = TABLE.split(doc)
    found = []
    for index, part in enumerate(parts):
        rows = detail_rows(part) if part.startswith("<table") else []
        names = names_before(re.sub(r"\s+", " ", text(parts[index - 1])), known) if rows else []
        if rows and len(names) != len(rows):
            print(f"unpaired table on {page}: {names}", file=sys.stderr)
            continue
        for name, values in zip(names, rows):
            type_no, code = known[name]
            if re.fullmatch(r"\d{8}|\d{13}", code):
                found.append(entry(page, url, name, type_no, code, values))
    return found


def main():
    cards = {}
    for page in PAGES:
        url, doc = get(page)
        found = parse(page, url, doc)
        print(f"{len(found):4d} cards  {page}", file=sys.stderr)
        for card in found:
            cards.setdefault(card["barcode"], card)
    json.dump(
        {
            "fetched_utc": datetime.now(UTC).strftime("%Y-%m-%d"),
            "source": BASE + urllib.parse.quote("カードリスト"),
            "cards": sorted(cards.values(), key=lambda r: r["barcode"]),
        },
        sys.stdout,
        ensure_ascii=False,
        indent=1,
    )


if __name__ == "__main__":
    main()
