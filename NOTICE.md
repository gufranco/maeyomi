# Third-party attribution

## Barcode Battler II Simulator

The decoder in `src/maeyomi/decoder/` is a port of the barcode reading
logic in `src/BarcodeRead.as` from:

- Project: Barcode Battler II Simulator
- Author: finalfighter
- Source: <https://github.com/finalfighter/BarcodeBattler2-Simulator>
- Licence: MIT

The card corpus in `tests/fixtures/simulator_corpus.json` is extracted from that
project's `bin-release/xml/` card lists.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Documentation sources

Attribute ranges, the read-type rule and the special ability table were taken
from <https://barcodebattler.net/>, which mirrors
<http://www.yuko2ch.net/barcode/>. The high health bonus sets, the hidden battle
values and the job 6 ruling follow <https://barcodebattler.net/page21.htm> and
the analysis at <https://note.com/sakigomyway_5634/n/n61808a7245e5>, whose
author tested printed codes on a device. Only facts are taken from either.

Card attribute fixtures in `tests/fixtures/wiki_cards.json` were taken from the
card lists on <https://wikiwiki.jp/barcode/>, with the source page and URL
recorded on every entry.

The barcodes and English names of the Zelda, Shogaku Ninensei and Street
Fighter II cards were taken from the card lists in
<https://www.barcodebattler.co.uk/deeta.js>. Only those facts are taken; none
of that script's code appears here.

## Datach Dragon Ball Z

The rule `src/maeyomi/datach/` reads a barcode by, and the numbers in
`dbz_tables.py`, were derived from the game's own program and confirmed against
the game running in MAME. No ROM bytes are shipped. The barcodes and names of
the 36 cards packed with the game come from the card list in
`src/gui/dlgDetachBarcode.cpp` of <https://github.com/punesemu/puNES>, which is
GPL-2 licensed. Only those facts are taken, and each one was checked by the
game itself; no code from puNES appears here.

## Not used

`VITIMan/barcode-battler-engine` is GPL-3 licensed. No code, structure or naming
from that project appears here. It is named only because its published card
values pointed at the wikiwiki.jp lists that this project fetches directly.

## Open Food Facts

The product shelf in `src/maeyomi/products/japan.json` holds barcodes,
product names and brand names for products sold in Japan, taken from:

- Project: Open Food Facts
- Source: <https://world.openfoodfacts.org/>
- Licence: Open Database License 1.0 (ODbL)
- Full text: <https://opendatacommons.org/licenses/odbl/1-0/>

The ODbL asks that the source be credited and that any redistributed database
stay under the same licence. That file is a subset of theirs and carries the
same terms; it is credited on the page that shows it and in the command line
that prints it. Every number on a card is read from the barcode by this
project's own decoder and is not part of their data.

The same project answers the `products lookup` path at
`src/maeyomi/products/lookup.py`, which names this project in its user
agent as their terms of use ask.
