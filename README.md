# Barcode Battler II card generator

Generate printable cards for the Barcode Battler II, either at random or built
to attributes you choose. Every barcode is produced by inverting the device's
real reading algorithm and is decoded back before it can reach a card.

Cards are verified three ways: against this project's own decoder, by
rasterising each printed page and reading the barcodes back with a real barcode
reader, and by reading printed cards on a physical Barcode Battler II. The
protocol and what each session settles are in
[`docs/hardware-validation.md`](docs/hardware-validation.md).

## Install

```bash
uv sync                  # command line only
uv sync --extra ui       # add the local web interface
```

## Use

A sheet of 24 random cards, nine to an A4 page, reproducible from a seed:

```bash
barcode-battler random --count 24 --hp 1000-10000 --st 100-3000 --df 100-3000 \
    --seed 1234 --output cards.pdf
```

One card built to an exact specification:

```bash
barcode-battler generate --name "Fire Knight" \
    --hp 5000 --attack 1800 --defense 1200 \
    --race human --class warrior --ability 17 \
    --output fire-knight.pdf
```

It prints what you asked for beside what came out, so a card that differs cannot
pass unnoticed:

```
Field    Requested       Generated       Difference
---------------------------------------------------
HP       5000            5000
ST       1800            1800
DF       1200            1200
Race     human           human
Class    warrior         warrior
Ability  17              17
```

Read a barcode the way the device reads it:

```bash
barcode-battler decode 0401207237501
```

The device carries numeric ability codes rather than named elements. List them:

```bash
barcode-battler abilities
```

A local page with the same two forms:

```bash
barcode-battler serve
```

Every stat option takes an exact value, a range, or a bound: `5000`,
`5000-6000`, `>=1500`, `<=3000`. Add `--images png` to export page images
beside the PDF.

When a request cannot be met exactly, `generate` says which field blocks it and
writes nothing. Add `--nearest` to get the closest reachable card instead:

```bash
barcode-battler generate --hp 20900 --st 11000 --df 10000 \
    --race mechanical --nearest --output golem.pdf
```

```
closest card differs by 100 across the requested stats
  df: requested 10000, produced 9900
```

The distance is the sum of the gaps on HP, ST and DF in displayed units,
counting only the stats the request constrained. Race, class, job, ability and
speed are never approximated: a request for a human is not better served by a
bird, so a request blocked on one of those comes back unsatisfied.

Add `--back-read` for a card the device reads from the back rather than the
front. Those carry lower ceilings, 49900 HP against 99900, and four digits feed
the stats and the ability jointly, so far fewer combinations are reachable.

## What the device actually stores

From [barcodebattler.net](https://barcodebattler.net/), reproduced by the
decoder rather than coded into it.

| Attribute | Front read | Back read |
|---|---|---|
| HP | 0 to 99900 | 0 to 49900 |
| ST | 0 to 19900 | 0 to 11900 |
| DF | 0 to 19900 | 0 to 9900 |
| Special ability | 00 to 99 | 00 to 29 |

Races 0 to 4 are characters: mechanical, animal, aquatic, bird, human. Races 5
to 9 are items. Job digits 0 to 6 are warriors, 7 to 9 are magicians. Values are
stored in units of 100, so every stat is a multiple of 100.

Two constraints surprise people, and the tool reports both rather than silently
producing something else:

- A character above 19900 HP needs the published front-read marker, which forces
  the third digit to 9. Such a card's HP always ends in 900, and its speed is
  always 5.
- Races 0, 1 and 2 have their strength and defence rewritten above 20000 HP, so
  not every pair of values is reachable at that size.

## How it works

```
requested attributes -> digit placement -> barcode -> decoder -> compare -> accept
```

The front reading maps fixed digit slices onto attributes, so inverting it is
placement rather than search: a fully specified request determines every digit
and the check digit is computed, leaving one candidate rather than the 10^12 a
brute force would walk. Every candidate still goes back through the decoder, and
one that disagrees on any field is discarded.

The back reading is not a bijection. Four digits feed hit points, strength,
defence and the ability jointly, and the race sits on the check digit position,
so it cannot be placed and has to be arrived at by tuning a free digit. The
reachable set is small enough to enumerate outright: 10000 digit combinations
produce 5000 distinct stat triples, because the hit point hundreds digit is
halved.

Barcodes are drawn as vectors at an explicit module width, defaulting to the EAN
nominal 0.33 mm. A rasterised barcode scaled to fit a layout rounds its modules
unevenly and stops scanning, which no test on the digit string would catch.

## Printing

Print at 100 percent. Turn off "fit to page", "shrink to fit" and any other
magnification. A scaled page still looks correct and still stops reading,
because the module width is what a scanner measures.

Each sheet carries a 100 mm ruler at its foot, numbered in centimetres, with a
line naming the width each barcode should measure. Hold a ruler against it after
the first print. If it comes out short, the printer scaled the page; correct the
dialog and print again. The band sits below the lowest card, so it leaves with
the offcut.

| Quantity | Printed | Source |
|---|---|---|
| Module width | 0.330 mm | GS1 EAN-13 nominal, SC2 |
| Bar height | 22.85 mm | GS1 nominal, and the whole of a hand swipe's vertical tolerance |
| Symbol width, quiet zones included | 37.29 mm | 113 modules |
| Card | 63.5 by 88.9 mm | Poker size, nine to an A4 page |
| Clearance around the symbol | 13.1 mm each side, 4.5 mm below | Well past the 3.6 mm quiet zone the standard requires |

The bar height is the number to watch. A point-of-sale scanner sweeps a beam
across a symbol many times a second; the Barcode Battler has a slot and a person
pushes the card through it by hand, so short bars are the failure nobody
notices. The renderer refuses a bar height below 80 percent of the nominal, and
the tests measure the data bars off a rendered page rather than trusting the
setting.

## The real cards

`barcode-battler official --list` names the fourteen card lists Epoch released
and how many cards of each will print; `barcode-battler official --set candy -o
candy.pdf` prints one, and leaving out `--set` prints all 572. The web page has
the same thing under **The real cards**.

Epoch never published a machine-readable list, so the barcodes come from the
pages where collectors typed in the cards they own, on
[wikiwiki.jp](https://wikiwiki.jp/barcode/). Every entry keeps the address of
its page. Five entries fail their own check digit, which means someone mistyped
a digit; the wrong one cannot be identified, so they are listed and left out
rather than repaired by guessing. The numbers printed on each card are read from
the barcode by this project's decoder, not copied from the wiki.

## The cheat code

`barcode-battler cheat -o cheat.pdf`, or type a code into the box at the foot of
the web page, or press up, up, down, down, left, right, left, right, B, A
anywhere on it. The card is a mechanical magician with 99900 health, 24500
attack, 19900 defence and its attack doubled.

It is found, not typed in: the generator walks every front-read fighter at full
health through the decoder's own arithmetic and keeps the strongest one that
avoids both unresolved overflow branches. The 24500 is above the 19900 that
barcodebattler.net publishes, because a mechanical fighter whose attack digits
fall in the dual bonus set collects two bonuses. The codes are a joke, not a
lock.

## Two languages and pictures

Every card is printed in English and Japanese, whichever language the page is
in. The kind of creature, how it fights, the three battle numbers, the special
power and the swipe caption all appear in both. Each fact also has a picture
for a child who reads neither yet: a coloured band with a pictogram for the kind
of creature, a heart, a sword and a shield for the numbers, and a pictogram for
the special power showing what it changes and which way, such as a sword with
an arrow up for "own attack doubled". The arrow's direction carries the
meaning, never its colour.

The special power text is the published wording in both languages: the Japanese
is copied from barcodebattler.net/page05.htm and the English is this project's
reading of the same page. The race, class and stat names are this project's own
translation, in the hiragana and katakana a young reader learns first. A
player's chosen name is printed as typed, in either script.

The web page switches between English and Japanese with the buttons at the top,
and remembers the choice.

Japanese is set in a font every PDF reader carries but which is referenced
rather than embedded. For a print shop, send the page images instead of the PDF,
`--images png`, which are 600 dpi with the lettering already drawn in.

## Colour

The cards go to a commercial printer, which often means the job runs in black
and white, and they are handed to children, roughly one boy in twelve of whom
does not see red and green apart. Both cases are handled by measurement.

Nothing is told apart by colour alone. Every band carries its own name and its
own pictogram, and every battle number carries its own shape and its two-letter
label, so a card read in grey loses decoration and no information.

`src/barcode_battler/rendering/colour.py` carries the arithmetic and
`tests/rendering/test_palette.py` holds the palette to it:

| Check | Threshold | Source |
|---|---|---|
| White text on a band, in colour and in grey | 4.5 to 1 | WCAG 2.2, contrast minimum |
| A pictogram against its tile, in colour and in grey | 3 to 1 | WCAG 2.2, non-text contrast |
| Two fighter bands, under normal vision and under protanopia, deuteranopia and tritanopia | 20 CIE 1976 units | The distance at which two colours read as different colours rather than two shades of one |
| Two fighter bands printed in grey | 1.15 to 1 | A visible tonal step |
| The one-use and permanent variants of a weapon or armour, in grey | 1.5 to 1 | They share a pictogram, so the tone has to carry more |

The dichromacy simulation is the linear approximation of Brettel, Vienot and
Mollon. A sheet is also rasterised, converted to grey, and every barcode on it
decoded, so the print survives the printer that has no colour at all.

## Where this came from

The decoder is a port of `src/BarcodeRead.as` from the MIT-licensed
[Barcode Battler II Simulator](https://github.com/finalfighter/BarcodeBattler2-Simulator).
Attribute ranges, the read-type rule and the ability table come from
[barcodebattler.net](https://barcodebattler.net/). Card fixtures come from the
card lists on [wikiwiki.jp](https://wikiwiki.jp/barcode/), with the source page
and fetch date recorded on every entry. Full attribution and the licence
boundary: [`NOTICE.md`](NOTICE.md).

Three behaviours are unresolved and recorded in
`src/barcode_battler/decoder/uncertainties.py`. The decoder reproduces all three
faithfully; the generator refuses to emit the two that would put an unverified
value on a printed card.

## Development

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest --cov
```

Fixtures are rebuilt with `uv run python tools/fetch_fixtures.py`.
