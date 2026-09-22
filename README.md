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
maeyomi random --count 24 --hp 1000-10000 --st 100-3000 --df 100-3000 \
    --seed 1234 --output cards.pdf
```

One card built to an exact specification:

```bash
maeyomi generate --name "Fire Knight" \
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
maeyomi decode 0401207237501
```

The device carries numeric ability codes rather than named elements. List them:

```bash
maeyomi abilities
```

A local page with the same two forms:

```bash
maeyomi serve
```

Every stat option takes an exact value, a range, or a bound: `5000`,
`5000-6000`, `>=1500`, `<=3000`. Add `--images png` to export page images
beside the PDF.

When a request cannot be met exactly, `generate` says which field blocks it and
writes nothing. Add `--nearest` to get the closest reachable card instead:

```bash
maeyomi generate --hp 20900 --st 11000 --df 10000 \
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

## The web interface

`maeyomi web` starts the local page and opens it, which is the same
program with pictures: every tab is a command, and every command is a tab.
`--no-open` starts it without a browser, and `maeyomi serve` is the
same thing for a machine that has none.

## Checking the machine

`maeyomi doctor` checks that this computer can print a card the device
will read, and says what it found rather than that it looked. It reads a
barcode whose answer is known, draws a symbol and decodes it back out of the
PDF, confirms the Japanese font resolved, re-measures the palette against its
contrast and colour-blindness thresholds, counts both card lists, and reports
what runs it, whether the terminal can print Japanese and how much room is
left. It exits non-zero only when something is genuinely wrong.

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

Cards print standing up, poker sized at 63.5 by 88.9 mm, nine to an A4 sheet.
That is the size card sleeves and guillotines are built for, and it is a choice
rather than a reproduction: Epoch never published the size of its own cards and
no collector page, auction listing or wiki records it. The size lives in
`CARD_WIDTH_MM` and `CARD_HEIGHT_MM` in
[`layout.py`](src/maeyomi/rendering/layout.py), and changing those two
numbers moves everything else, because the grid, the gutters, the marks and the
fit check are all derived from them.

Each sheet follows what print shops ask for:

| Measure | Value | Why |
|---|---|---|
| Bleed | 1.5 mm on a sheet, 3 mm with `--print-shop` | A cut that lands a fraction off still finds ink |
| Gutter between cards | 4 mm, twice the bleed | Each card is cut on its own line, not one shared with its neighbour |
| Safe area | 4 mm from the trim | Nothing a reader needs sits where a trim can take it |
| Crop marks | Corner ticks starting at the bleed edge | What a printer cuts to, with no line crossing the card |
| Module width | 0.330 mm | GS1 EAN-13 nominal |
| Bar height | 22.85 mm | GS1 nominal, and the whole of a hand swipe's tolerance |

`--print-shop` writes the other shape the same cards take: one card per page,
the page sized to the card plus a 3 mm bleed, no ruler and no marks, which is
what a commercial printer's own instructions ask for.

Each sheet carries a 100 mm ruler at its foot, numbered in centimetres, and a
line above the cards, in English and Japanese, naming the width each barcode
should measure. Hold a ruler against it after the first print. If it comes out
short, the printer scaled the page; correct the dialog and print again. Both
bands sit outside the card grid, so they leave with the offcut.

## Reading a barcode you already have

`maeyomi decode 4901085061169` prints what the device would make of any
barcode, and `-o card.pdf --name "Tomato sauce"` prints the card as well. The
web page has the same thing under **Read a barcode**: type the digits printed
under the bars, and it shows the kind of card, the three numbers, the special
power and whether the device reads it from the front or the back, with a card
you can print.

`maeyomi kinds` lists every kind of card the device knows, in both
languages, with what each one does.

This is how the machine was actually played. Any product barcode is a card, so a
bottle of tomato sauce is a fighter and a packet of crisps is a weapon. Japanese
product codes work like any other: `4902102072618`, a bottle of tea, is armour
worth 2400 defence.

## The supermarket

`maeyomi products --search 茶` lists the real Japanese groceries that
match, `--count 9 --seed 3` takes a handful at random, and `-o shopping.pdf`
prints them. The web page has the same thing under **The supermarket**, with a
**Surprise me** button. Tomato sauce against noodles is a fair fight, and this
is the joke the machine was built on.

The shelf is a curated subset of [Open Food Facts](https://world.openfoodfacts.org/),
kept to barcodes issued to Japanese companies, the 45 and 49 prefixes, with a
name written in Japanese that the decoder accepts. Their data is published under
the Open Database License and this subset carries the same terms; see
[NOTICE.md](NOTICE.md). Nothing on a card comes from them: every number is read
off the barcode by this project's decoder, so a wrong name spoils a joke and
nothing else.

`maeyomi decode <barcode>` on the web page also asks Open Food Facts
what a barcode is called, and fills the name in when it knows. It is a
convenience: the lookup failing changes nothing about the card.

## The real cards

`maeyomi official --list` names the fourteen card lists Epoch released
and how many cards of each will print; `maeyomi official --set candy -o
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

`maeyomi cheat -o cheat.pdf`, or press the row of arrows at the foot of
the web page, or type up, up, down, down, left, right, left, right, B, A
anywhere on it. The card is a mechanical magician with 99900 health, 24500
attack, 19900 defence and its attack doubled.

It is found, not typed in: the generator walks every front-read fighter at full
health through the decoder's own arithmetic and keeps the strongest one that
avoids both unresolved overflow branches. The 24500 is above the 19900 that
barcodebattler.net publishes, because a mechanical fighter whose attack digits
fall in the dual bonus set collects two bonuses.

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

## Getting at it without a mouse or without sight

The page answers to a keyboard alone. A skip link jumps past the masthead, the
five tabs are one stop with the arrow keys moving between them, Home and End go
to the ends, every control paints a visible focus ring, every control is at
least 44 by 44 pixels, and the list of groceries can be scrolled from the
keyboard. The language switch changes the `lang` on the document, so a screen
reader changes voice with it. Animation is dropped when the system asks for
less of it.

axe-core reports no violation on any of the five tabs, in the light scheme and
in the dark one, against WCAG 2.2 A and AA plus its own best-practice set. The
checks that a rule set cannot make were made by hand in a real browser: the
focus ring was read back off the focused element rather than off the
stylesheet, and the cheat hint in the footer measures 7.43:1 against the page.

The PDFs carry what a PDF can carry without a structure tree. Each one names
itself, so a reader announces "Barcode Battler II card: Tea" instead of
`sheet.pdf`, and is told to prefer that title over the filename. The document
declares its language, its author and what it is. Every word on a card is real
text: the names, the numbers, the special power, both languages, and the digits
under the bars, all of which come back out of the file in the order a person
would read them, kind first, then the name, then each number after the label
that says what it measures, then the power, and the barcode last.

What is not there: ReportLab emits no tag tree, so these are not PDF/UA files.
There are no headings, no lists and no alternative text for the pictograms, and
the Japanese runs are not individually marked as Japanese. The pictograms
repeat what the words next to them already say, so nothing is lost by their
having no description, but a validator will call these untagged, and it is
right.

## Colour

The cards go to a commercial printer, which often means the job runs in black
and white, and they are handed to children, roughly one boy in twelve of whom
does not see red and green apart. Both cases are handled by measurement.

Nothing is told apart by colour alone. Every band carries its own name and its
own pictogram, and every battle number carries its own shape and its two-letter
label, so a card read in grey loses decoration and no information.

`src/maeyomi/rendering/colour.py` carries the arithmetic and
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
`src/maeyomi/decoder/uncertainties.py`. The decoder reproduces all three
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
