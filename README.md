<div align="center">

# maeyomi

<strong>Print playable cards for Barcode Battler machines and barcode games.</strong>

English &nbsp;|&nbsp; [日本語](README.ja.md)

[![ci](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml/badge.svg)](https://github.com/gufranco/maeyomi/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](#development)
[![python](https://img.shields.io/badge/python-3.14-blue)](pyproject.toml)

<p align="center">
  <a href="#install">Install</a> &nbsp;|&nbsp;
  <a href="#open-it">Open it</a> &nbsp;|&nbsp;
  <a href="#from-the-command-line">Command line</a> &nbsp;|&nbsp;
  <a href="#how-it-works">How it works</a> &nbsp;|&nbsp;
  <a href="#the-supermarket">The supermarket</a> &nbsp;|&nbsp;
  <a href="#where-this-came-from">Sources</a>
</p>

</div>

**1025** official cards transcribed. **2958** Japanese groceries. **100** special powers. Two languages on every card. **100%** test coverage. Barcode Battler II cards verified on the real machine.

---

The Barcode Battler II reads a barcode and derives a fighter or an item from
the digits alone. Maeyomi is the device's own word for the front read, the one
that produces a fighter. This program inverts that arithmetic: ask for a 2400
defence armour card and it works out which barcode the device would read that
way, then prints it.

Every barcode is decoded again before it reaches paper, and every printed page
is rasterised and read back with a barcode reader. Printed cards were swiped on
a physical Barcode Battler II.

The first Barcode Battler, from 1991, reads the same digits its own way: every
fighter is a warrior, health stops at 19900, attack and defence at 9900, and the
two-digit code is a flag from a different table, so 18 is the hero where the II
doubles the attack. Add `--device bb1` to `decode`, `generate` and `cheat` to
make cards for it. Its decoder reproduces 113 published cards from the four
lists written for it, and no card for it has been read on a physical first
Barcode Battler yet, which every sheet for it says.

The Barcode Battler II Double, the II² of 1993, has no reader and takes codes
from a II. It reads them the II's way, except a code that starts with 7 and has
8 as its tenth digit, which it reads its own way: attack and defence reach
99900, and the special power is two of the health's digits.
`--device double` makes cards for it, using "BBIIダブルC0" on
[barcodebattler.net](https://barcodebattler.net/bb2c0.html) as its source. That
reading explains the eleven cards of the 正伝3 list that no II reading could.
The Double also names two classes the II does not, the priest for job 4 and the
holy warrior for job 6, and has its own table of special powers.

Bandai's Datach Dragon Ball Z: Gekitou Tenkaichi Budoukai, a Famicom game of
1992, came with a barcode reader. `--device dbz` makes cards for it. The game
scatters the bits of ten digits into a 40-bit number and reads a fighter or an
item, a special move level, HP, BP and DP from it. That rule was read out of
the game's own program, and the decoder agrees with the game running in MAME on
every one of the 232 codes the game accepted there. Pick the fighter or item
with `--character`, by the name the game shows or by its id, the level with
`--level`, and the numbers with `--hp`, `--bp` and `--dp`, adding `--nearest`
to take the closest printable card when those exact numbers cannot print; a fighter whose
numbers are high enough turns into its stronger form, as the game does. No card
for it has been read by a physical Datach yet, which every sheet for it says.

Datach Ultraman Club: Supokon Fight!, Bandai's second Datach game, of 1993,
reads a barcode into one of 51 types, Ultra heroes and monsters from 0 to 27
and items from 32 up, and three numbers it calls PW, ST and SP, each 0 to 9900
in steps of 100. `--device ultraman` makes cards for it: pick the type with
`--character`, by the name the game shows or by its number, and the three
numbers with `--hp`, `--st` and `--df` in that order. Every value in that range
prints. The rule was read out of the game's program and agrees with the game
itself, running in MAME, on its 38 released cards and on 51 codes built one per
type. No card for it has been read by a physical Datach yet.

Datach SD Gundam: Gundam Wars, also of 1993, reads a barcode as one of 63 mobile
suits or one of 59 command cards. A mobile suit starts from its own HP, AP, DP
and CP, adds a bonus from a table to each, and carries one of two short-range
and one of two long-range weapons; a command card carries its effect and the
CP it costs. `--device sdgundam` makes cards for it: pick the card with
`--character`, by name, model number or number, the numbers with `--hp`,
`--st` and `--df`, which are HP, AP and DP, and the weapons and CP with
`--pick sr=1`, `--pick lr=5` or `--pick cp=11`. A number between two the game
can hold becomes the closest one, and the command says so. The rule agrees
with the game in MAME on its 76 released barcodes and on 122 codes built one
per slot. No card for it has been read by a physical Datach yet.

Datach Yu Yu Hakusho: Bakutou Ankoku Bujutsukai, also of 1993, reads a barcode
as one of 22 fighters or 10 items, and one more fighter the game hides. A
fighter's HP and SP are its own and no barcode changes them; what the barcode
chooses is which of its four techniques it can use. An item adds HP or SP by
one of four levels, or changes a rule of versus mode. `--device yuyu` makes
cards for it: pick the card with `--character`, its techniques with `--pick
moves=15`, one bit per technique, and an item's level with `--pick level=3`.
The rule agrees with the game in MAME on its 37 released cards and on 183
codes built across every character, mask and item. No card for it has been
read by a physical Datach yet.

Datach J.League Super Top Players, of 1994, reads a barcode as one of the 150
players of the 1993 J.League's ten clubs, or as one of those clubs. A card
names a real player and carries no numbers of its own, so the game keeps each
player's abilities and there is no cheat card for it. `--device jleague` makes
cards for it: pick the player or club with `--character`, by name or number.
The rule agrees with the game in MAME on its 160 released barcodes and on 12
codes built to reach every folded value the game allows. No card for it has
been read by a physical Datach yet.

Two Datach games cannot take a card. Crayon Shin-chan: Ora to Poi Poi has no
barcode reading in its program at all, and Battle Rush: Build Up Robot
Tournament needs a save chip MAME does not fully emulate and has no known card
list, so it is not supported yet.

## Install

```bash
brew tap gufranco/maeyomi https://github.com/gufranco/maeyomi
brew install gufranco/maeyomi/maeyomi
```

The tap is this repository. Homebrew wants the explicit URL because the repo is
not called `homebrew-maeyomi`, which keeps the formula, the source and the
release beside each other instead of in a second repo that drifts.

Installing pulls in Python 3.14 and builds an isolated environment from the
committed lockfile, so you get the versions the tests ran against and nothing
lands in your own Python.

From a checkout instead, `uv sync --extra ui` and put `uv run` in front of
every command below.

## Open it

```bash
maeyomi web
```

That starts a local page and opens your browser at it. Everything the program
does is in there, so nothing below this point is required reading. The page
says what it is for in a line:

> Playable cards for Barcode Battler machines and barcode games, printed in English and Japanese.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/one-card-dark.png">
  <img alt="The card maker, with a fighter designed on the left and the printable card drawn on the right" src="assets/screenshots/one-card-light.png">
</picture>

Design a fighter with the sliders, watch the card redraw as you move them, and
print it. The panel underneath says whether the machine will read back exactly
the numbers you asked for, and shows the barcode it worked out.

**Machine or game**, under the title, picks what the cards are for: the
Barcode Battler II, the first Barcode Battler, the Double, Datach Dragon Ball
Z, Datach Ultraman Club, Datach SD Gundam Wars, Datach Yu Yu Hakusho or
Datach J.League. Every tab follows it: the card maker shows only the fields that device reads
and stops its sliders at the device's limits, the random sheet and the
supermarket read each barcode the way that device does, **The real cards**
lists only that device's sets and hides the set picker when there is one, and
the cheat code is that device's strongest card. The same barcode is a
different card on each device. On the command line, `--device` does the same
for `generate`, `decode`, `cheat`, `random`, `products`, `kinds`, `abilities`
and `official`.

**Any barcode you already own is also a card.** Type the digits from the
shopping into **Read a barcode** and the page shows what the device makes of
it. This one is a bottle of Coca-Cola, which the machine reads as armour worth
2400 defence.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/read-a-barcode-dark.png">
  <img alt="A bottle of Coca-Cola typed in as a barcode, read back as an armour card worth 2400 defence" src="assets/screenshots/read-a-barcode-light.png">
</picture>

**The supermarket** holds 2958 real Japanese groceries, so a game can be played
without a shopping trip. Search it, or press **Surprise me** and print the nine
you get.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/screenshots/supermarket-dark.png">
  <img alt="The supermarket tab, listing real Japanese groceries with the stats the device reads from each barcode" src="assets/screenshots/supermarket-light.png">
</picture>

The other two tabs print a sheet of random cards and the 1025 cards Epoch and
Bandai actually released. The page is in English and Japanese, and switches with the
buttons at the top.

`maeyomi web --no-open` starts the server without a browser, and `maeyomi
serve` is the same thing for a machine that has none.

## From the command line

Every tab above is also a command.

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
PP       any             5
MP       any             0
Race     human           human
Job      -               0
Class    warrior         warrior
Speed    -               0
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

Items are built the same way. A weapon carries only attack, armour only
defence, and a helper item one thing: health, herbs or magic points. Herbs and
magic points are plain counts from 0 to 99:

```bash
maeyomi generate --name "Herb Pouch" --race support_item --herbs 99 \
    --output herbs.pdf
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

## Checking the machine

`maeyomi doctor` checks that this computer can print a card the device will
read, and prints what each check saw. It reads a barcode whose answer is known,
draws a symbol and decodes it back out of the PDF, confirms the Japanese font
resolved, re-measures the palette against its contrast and colour-blindness
thresholds, counts both card lists, and reports what runs it, whether the
terminal can print Japanese and how much room is left. It exits non-zero only
when something is genuinely wrong. Run it first, either way: a font that did
not resolve otherwise shows up as blank text on a printed card.

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

Two constraints narrow what can be asked for. A request that hits either one is
refused with the reason, never quietly altered:

- A character above 19900 HP needs the published front-read marker, which forces
  the third digit to 9. Such a card's HP always ends in 900, and its speed is
  always 5.
- Races 0, 1 and 2 have their strength and defence rewritten above 20000 HP, so
  not every pair of values is reachable at that size. Some of those codes make
  the device fight with more attack or defence than it displays, up to 24600;
  the card prints that value too.

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
That is the size card sleeves and guillotines are built for. It is this
project's choice: Epoch never published the size of its own cards, and no
collector page, auction listing or wiki records it. The size lives in
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
**Surprise me** button. Tomato sauce against noodles is a fair fight.


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

`maeyomi official --list` names the 27 card lists Epoch and Bandai released,
how many cards of each will print, and which device each list was written for; `maeyomi official --set candy -o
candy.pdf` prints one, and leaving out `--set` prints all 1025. The web page has
the same thing under **The real cards**.

Epoch never published a machine-readable list, so the barcodes come from the
pages where collectors typed in the cards they own, on
[wikiwiki.jp](https://wikiwiki.jp/barcode/). Every entry keeps the address of
its page. Five entries fail their own check digit, which means someone mistyped
a digit; the wrong one cannot be identified, so they are listed and left out
rather than repaired by guessing. The numbers printed on each card are read from
the barcode by this project's decoder, not copied from the wiki.

Six lists were written for the first Barcode Battler: the original set, The
Demon Army God Mars Appears, Chuhai Khan Strikes Back, The Final Battle: God
versus Mother, the candy cards, and CoroCoro Comic's Obocchama-kun cards, which
say they work with the Barcode Battler rather than the II. Four describe the flags with the first
device's table; the God Mars list prints no numbers, and it has no magician and
no herb or magic item, which only the II reads. The 正伝3 and 正伝4 lists need
the Barcode Battler II Double's 7-read, which half of 正伝4's cards use. The
other 15 print with the II's.

The Zelda, Shogaku Ninensei magazine and Street Fighter II cards come from the
card lists in [barcodebattler.co.uk](https://www.barcodebattler.co.uk/)'s
`deeta.js`, which publishes them in English, so those cards carry English
names. One Zelda item, the red potion, is also a card of the II board game.

The Dragon Slayer, Doraemon: Nobita's Dinosaur, Obocchama-kun and Meiji cards
had no transcription anywhere, so their barcodes were read off the card scans
[barcodebattler.co.uk publishes](https://www.barcodebattler.co.uk/scans/Japan/),
one card at a time, and each was tied to its name by the numbers printed on
its front. Only the Meiji cards numbered 1 and 5 have been scanned. The Super
Mario World cards are known only from their fronts, which carry no barcode, so
they cannot be printed yet.

Datach Dragon Ball Z came with 40 cards. Its
[manual](https://setsumei.cloudfree.jp/famicom/datachdragonballz/datachdragonballz.html)
says some of them, Super Saiyan Goku, Super Saiyan Trunks, final-form Frieza and
Perfect Cell among them, carry no barcode, and asks players to stick one of their
own on those. The 35 that carry one, plus a special Super Saiyan Goku card, are
the 36 printed here, taken from the list in the
[puNES](https://github.com/punesemu/puNES) emulator's source and each read by
the game in MAME before it was added.

The game reads a barcode only when its bars, and its spaces, come in at least
three different widths; it sorts the widths it measures into classes in its
program at $B085 and refuses a scan with fewer. A code whose three widths are
1, 2 and 4 reads only at some swipe speeds. Every code this program builds for
the game reads at any speed, `maeyomi decode --device dbz` names a code the
game refuses, and the supermarket marks the products it cannot read.

Datach Ultraman Club came with 40 cards, two of them blank. The other 38 are
the codes [retrostuff.org](https://retrostuff.org/2019/03/23/bandai-datach-ultraman-club-spokon-fight-barcodes-for-mame/)
read off a boxed set, named as the puNES list names them, and each read by the
game in MAME. The later Datach games do not refuse a code the way Dragon Ball
Z does: they read codes whose bars come in only two widths. What they share is
trouble with a code whose bars or spaces are exactly 1, 2 and 4 modules wide,
which reads only at some swipe speeds; five of the released Ultraman Club cards
are such codes. Every card this program builds for a Datach game avoids them.

SD Gundam Wars came with 40 cards. 37 of them carry two barcodes, a mobile suit
on the bottom edge and a command on the top, and a special card carries one of
each: 76 barcodes, which [retrostuff.org](https://retrostuff.org/2019/05/12/bandai-datach-sd-gundam-gundam-wars-barcodes-for-mame/)
read off a boxed set, matching the puNES list, and each read by the game in MAME.

Yu Yu Hakusho came with 40 cards, three of them without a barcode. The other 37
come from the spreadsheet [archive.org](https://archive.org/details/yu-yu-hakusho-bakuto-ankoku-bujutsue-box-front)
keeps beside its scans of a complete set, named as that spreadsheet names them,
and each was read by the game in MAME.

J.League Super Top Players came with 40 cards, each carrying four barcodes, a
club and three players or four players. The 160 barcodes come from the
spreadsheet [archive.org](https://archive.org/details/j-league-super-top-players-manual)
keeps beside its scans of a complete set, are named as the game's own player
directory names them, and each was read by the game in MAME.

## The cheat code

`maeyomi cheat -o cheat.pdf`, or press the row of arrows at the foot of
the web page, or type up, up, down, down, left, right, left, right, B, A
anywhere on it. The card is a mechanical magician with 99900 health and its
attack doubled. The device displays 14600 attack and 19900 defence, and fights
with 24600 attack.

Nothing about it is hardcoded. The generator walks every front-read fighter at
full health through the decoder's own arithmetic and keeps the one that fights
with the most attack and defence together, avoiding every unresolved branch.
The hidden 24600 is the device's own: a mechanical fighter above 20000 health
whose attack digits are 46 gains a bonus the display never shows. A device was
seen doing exactly that with the code 4994699095453, per
[barcodebattler.net](https://barcodebattler.net/page21.htm). The card prints the
hidden value beside its special power.

`maeyomi cheat --items -o cheat.pdf` adds five items at the most their digits
can hold: a weapon of 9900 attack, armour of 9900 defence, a potion of 99900
health, 99 herbs and 99 magic points. Each passes a different documented power
to whoever uses it: the opponent's defence cut by 80 percent, your own defence
up by half, the opponent's health halved, the opponent's attack halved, and the
opponent's special powers cancelled. Whether the powers of several items add up
is not documented, so none of this relies on it.

The command says which jobs can use each item, from the equipment table in the
[note.com analysis](https://note.com/sakigomyway_5634/n/n61808a7245e5). No
magician can hold a weapon or armour, so the blade and the shield are for a
warrior of any job, while the potion, the herbs and the crystal all work with
the cheat magician.

`maeyomi cheat --device bb1 --items -o cheat.pdf` does the same for the first
Barcode Battler: a warrior with every number at its ceiling, 19900 health, 9900
attack and 9900 defence, and its attack doubled, plus a weapon, armour and a
potion at their ceilings. The warrior is job 9, which that device lets equip
every weapon and gives weapons of types 0 to 4 half as much attack again.

`maeyomi cheat --device double --items -o cheat.pdf` is the strongest of the
three: a Double card with 99900 attack and 99900 defence, the ceiling that
source states, and the power that halves the opponent's health. That power is
two of the health's digits, so it leaves 92900 health. The items are the II's,
each carrying a power from the Double's own table. No equipment table for the
Double has been published, so the command does not say which job can use
which item.

`maeyomi cheat --device dbz --items -o cheat.pdf` is Super Saiyan Goku at
special move level 3 with 99500 HP, 48250 BP and 33250 DP. HP is the most the
game's rule can carry; BP and DP are the strongest pair whose barcode still
comes out as ten decimal digits, found by a search over every printable card.
That is more than ten times the card the game hides in its own program. The
items are one of each strongest effect: the senzu bean, Shenron, Kami, Guru,
ultra divine water and Porunga at level 4.

`maeyomi cheat --device ultraman -o cheat.pdf` is Ultraman with PW, ST and SP
all at 9900, the most the game's two tables can add up to.

`maeyomi cheat --device sdgundam -o cheat.pdf` is the Quin Mantha, the mobile
suit with the most HP, AP and DP together, with every bonus at its top: HP
7700, AP 7000, DP 9000 and CP 6.

`maeyomi cheat --device yuyu -o cheat.pdf` is the fighter the game hides, SP
Toguro, with 9999 HP, 9999 SP and all four of his techniques. The game gives it
for one exact stream of bits, which no card Bandai printed carries.

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
having no description. A validator will call these untagged.

## Colour

The cards go to a commercial printer, which often means the job runs in black
and white, and they are handed to children, roughly one boy in twelve of whom
does not see red and green apart. Both cases are handled by measurement.

Nothing is told apart by colour alone. Every band carries its own name and its
own pictogram, and every battle number carries its own shape and its two-letter
label, so a card printed in grey still says everything it said in colour.

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

Where the sources disagree, the question is recorded in
`src/maeyomi/decoder/uncertainties.py` with what each source says and what was
chosen. The decoder follows the simulator except where sources that tested
printed codes on a device say otherwise: the high health bonus follows
[barcodebattler.net](https://barcodebattler.net/page21.htm) and a
[note.com analysis](https://note.com/sakigomyway_5634/n/n61808a7245e5), and job 6
is a warrior. Five of the recorded questions would put an unverified value on
a printed card, and the generator refuses to emit any code that reaches them.

## Development

```bash
uv run ruff format .
uv run ruff check .
uv run pyright
uv run pytest --cov
```

Fixtures are rebuilt with `uv run python tools/fetch_fixtures.py`. The Datach
Dragon Ball Z record comes from `uv run python tools/oracle/record_dbz.py`, which
needs MAME and a dump of your own cartridge whose SHA-256 matches
[`artifacts.manifest.json`](artifacts.manifest.json); MAME runs without a window.
The later games' records come from `uv run python tools/oracle/record_game.py`
with `--game`, under the same conditions.

With `maeyomi serve` running, `node tools/render/layout.e2e.mjs` drives the
page in a real browser through `agent-browser`: no tab may scroll sideways at
320 or 1280 pixels, the device switch must show each device's fields, and the
notes must be visible and link their sources.
