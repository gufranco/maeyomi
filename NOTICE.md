# Third-party attribution

## Barcode Battler II Simulator

The decoder in `src/barcode_battler/decoder/` is a port of the barcode reading
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
<http://www.yuko2ch.net/barcode/>. Card attribute fixtures in
`tests/fixtures/wiki_cards.json` were taken from the card lists on
<https://wikiwiki.jp/barcode/>, with the source page and URL recorded on every
entry.

## Not used

`VITIMan/barcode-battler-engine` is GPL-3 licensed. No code, structure or naming
from that project appears here. It is named only because its published card
values pointed at the wikiwiki.jp lists that this project fetches directly.
