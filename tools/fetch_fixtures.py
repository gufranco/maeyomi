import html
import json
import re
import subprocess
import sys
import urllib.parse
from datetime import UTC, datetime

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0 Safari/537.36"
)
BASE = "https://wikiwiki.jp/barcode/"
INDEX = "カードリスト"

ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
TABLE = re.compile(r"<table.*?</table>", re.S)

HEADERS = {
    "名前": "name",
    "タイプNo.": "type_no",
    "コード": "barcode",
    "HP": "hp",
    "ST": "st",
    "DF": "df",
    "DX": "dx",
    "種族・種別": "race",
    "職業・種類": "job",
    "特殊能力": "special",
}
REQUIRED = ("barcode", "hp", "st", "df", "race", "special")


def get(page):
    url = BASE + urllib.parse.quote(page)
    out = subprocess.run(["curl", "-sL", "-A", UA, url], capture_output=True, check=True).stdout
    return url, out.decode("utf-8", "replace")


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xa0", " ").strip()


def cells(tr):
    return [text(c) for c in CELL.findall(tr)]


def num(x):
    x = x.replace(",", "").strip()
    return int(x) if re.fullmatch(r"-?\d+", x) else None


def lead(x):
    m = re.match(r"\s*(-?\d+)", x)
    return int(m.group(1)) if m else None


def parse(page, url, doc):
    stats, corpus, cols, full = [], [], None, False
    for tr in ROW.findall(doc):
        c = cells(tr)
        mapped = {HEADERS[h]: i for i, h in enumerate(c) if h in HEADERS}
        if "barcode" in mapped and not any(re.fullmatch(r"\d{8}|\d{13}", x) for x in c):
            cols, full = mapped, all(k in mapped for k in REQUIRED)
            continue
        if not cols or len(c) <= cols["barcode"]:
            continue
        code = c[cols["barcode"]].strip()
        if not re.fullmatch(r"\d{8}|\d{13}", code):
            continue
        entry = {
            "barcode": code,
            "name": c[cols["name"]] if "name" in cols and len(c) > cols["name"] else "",
            "type_no": c[cols["type_no"]] if "type_no" in cols and len(c) > cols["type_no"] else "",
            "source_page": page,
            "source_url": url,
        }
        if not full or max(cols.values()) >= len(c):
            corpus.append(entry)
            continue
        vals = {
            "hp": num(c[cols["hp"]]),
            "st": num(c[cols["st"]]),
            "df": num(c[cols["df"]]),
            "dx": num(c[cols["dx"]]) if "dx" in cols else None,
            "race": lead(c[cols["race"]]),
            "job": lead(c[cols["job"]]) if "job" in cols else None,
            "special": lead(c[cols["special"]]),
        }
        if any(vals[k] is None for k in ("hp", "st", "df", "race", "special")):
            corpus.append(entry)
            continue
        stats.append(entry | vals)
    return stats, corpus


def main():
    _, idx = get(INDEX)
    pages = [
        urllib.parse.unquote(p)
        for p in sorted(set(re.findall(r'href="/barcode/([^":?]+)"', idx)))
        if "カードリスト" in urllib.parse.unquote(p)
    ]
    all_stats, all_corpus = [], []
    for page in pages:
        url, doc = get(page)
        s, c = parse(page, url, doc)
        print(f"{len(s):4d} stats {len(c):4d} corpus  {page}", file=sys.stderr)
        all_stats += s
        all_corpus += c

    stats = {}
    for r in all_stats:
        stats.setdefault(r["barcode"], r)
    corpus = {r["barcode"]: r for r in all_corpus if r["barcode"] not in stats}

    print(f"unique: {len(stats)} with stats, {len(corpus)} corpus only", file=sys.stderr)
    json.dump(
        {
            "fetched_utc": datetime.now(UTC).strftime("%Y-%m-%d"),
            "source": BASE + urllib.parse.quote(INDEX),
            "cards": sorted(stats.values(), key=lambda r: r["barcode"]),
            "corpus": sorted(corpus.values(), key=lambda r: r["barcode"]),
        },
        sys.stdout,
        ensure_ascii=False,
        indent=1,
    )


main()
