"""The single page the local interface serves.

One file, no build step, no framework. The page calls the same endpoints a
script would.
"""

from barcode_battler.cli.report import DISCLAIMER

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Barcode Battler II card generator</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, sans-serif; margin: 0 auto; max-width: 52rem;
         padding: 1.5rem; line-height: 1.5; }
  h1 { font-size: 1.4rem; }
  fieldset { border: 1px solid currentColor; border-radius: 6px; margin: 0 0 1.5rem; }
  legend { padding: 0 .4rem; font-weight: 600; }
  label { display: inline-block; margin: .3rem .8rem .3rem 0; }
  label span { display: block; font-size: .8rem; }
  input { padding: .3rem; min-width: 8rem; }
  input[type="checkbox"] { min-width: 0; margin-right: .4rem; }
  :focus-visible { outline: 3px solid currentColor; outline-offset: 2px; }
  button { padding: .5rem 1rem; font-size: 1rem; cursor: pointer; }
  pre { background: rgba(127,127,127,.15); padding: .8rem; overflow-x: auto; }
  .note { font-size: .85rem; opacity: .8; }
</style>
</head>
<body>
<h1>Barcode Battler II card generator</h1>
<p class="note">__DISCLAIMER__</p>

<form id="custom">
  <fieldset>
    <legend>One card</legend>
    <label>Name <span>printed only</span><input name="name" value="Fire Knight"></label>
    <label>HP <span>5000 or 5000-6000</span><input name="hp" value="5000"></label>
    <label>ST <span>attack</span><input name="st" value="1800"></label>
    <label>DF <span>defense</span><input name="df" value="1200"></label>
    <label>Race <span>by name</span><input name="race" value="human"></label>
    <label>Class <span>warrior or magician</span><input name="class"></label>
    <label>Job <span>0-9</span><input name="job" type="number" min="0" max="9"></label>
    <label>Speed <span>0-9</span><input name="speed" type="number" min="0" max="9"></label>
    <label>Ability <span>code 0-99</span>
      <input name="ability" type="number" min="0" max="99"></label>
    <p>
      <label><input name="nearest" type="checkbox" value="1">
        Offer the closest card when the exact one is impossible</label>
    </p>
    <p>
      <label><input name="backRead" type="checkbox" value="1">
        Build a card the device reads from the back</label>
    </p>
    <p><button type="submit">Check</button>
       <button type="button" id="custom-pdf">Download PDF</button></p>
  </fieldset>
</form>

<form id="random">
  <fieldset>
    <legend>Random sheet</legend>
    <label>Count <input name="count" type="number" min="1" max="200" value="9"></label>
    <label>Seed <span>repeat a run</span><input name="seed" type="number"></label>
    <label>HP <input name="hp" value="1000-10000"></label>
    <label>ST <input name="st" value="100-3000"></label>
    <label>DF <input name="df" value="100-3000"></label>
    <label>Race <input name="race"></label>
    <p><button type="submit">Download PDF</button></p>
  </fieldset>
</form>

<h2>Result</h2>
<pre id="out">Nothing yet.</pre>

<script>
const out = document.getElementById('out');
const numeric = ['count', 'seed', 'job', 'speed', 'ability'];
const flags = ['nearest', 'backRead'];

function body(form) {
  const data = {};
  for (const [key, value] of new FormData(form).entries()) {
    if (value === '') continue;
    if (flags.includes(key)) { data[key] = true; continue; }
    data[key] = numeric.includes(key) ? Number(value) : value;
  }
  return data;
}

async function show(response) {
  out.textContent = JSON.stringify(await response.json(), null, 2);
}

async function download(url, payload, filename) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) { await show(response); return; }
  const link = document.createElement('a');
  link.href = URL.createObjectURL(await response.blob());
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
  out.textContent = 'Downloaded ' + filename;
}

document.getElementById('custom').addEventListener('submit', async (event) => {
  event.preventDefault();
  const response = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body(event.target)),
  });
  await show(response);
});

document.getElementById('custom-pdf').addEventListener('click', () => {
  download('/api/sheet', { cards: [body(document.getElementById('custom'))] }, 'card.pdf');
});

document.getElementById('random').addEventListener('submit', (event) => {
  event.preventDefault();
  download('/api/random', body(event.target), 'cards.pdf');
});
</script>
</body>
</html>
""".replace("__DISCLAIMER__", DISCLAIMER)
