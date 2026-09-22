const HIGH_HP = 20000;
const MARKER_REMAINDER = 900;
const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

const KONAMI = [
  'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
  'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a',
];
const SHAKE_MS = 700;
const CHEAT_QUIPS = [
  'The machine is sweating.',
  'Please do not tell the other fighters.',
  '99900 health. Your friends will need a bigger calculator.',
  'Attack doubled, because normal attack was just not enough.',
  'Warning: may cause your friends to stop playing with you.',
  'The barcode is real. The fairness is not.',
];
const WRONG_CODE_REPLIES = [
  'Nice try. The machine is not impressed.',
  'Nope. Maybe ask a grown-up who played in 1992?',
  'That is not it. The machine yawns.',
];

let cheatCard = null;

const $ = (id) => document.getElementById(id);

const pick = (items) => items[Math.floor(Math.random() * items.length)];

const escapeHtml = (text) => String(text).replace(/[&<>"']/g, (ch) => ESCAPES[ch]);

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const isJson = response.headers.get('content-type')?.includes('json');
  return { ok: response.ok, body: isJson ? await response.json() : null, response };
}

function reasons(body) {
  const detail = body?.detail;
  if (Array.isArray(detail)) return detail.map(String);
  if (typeof detail === 'string') return [detail];
  return ['Something went wrong. Please try different numbers.'];
}

function setStatus(id, kind, label, message, items = []) {
  const list = items.length
    ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`
    : '';
  const node = $(id);
  node.setAttribute('class', `status is-${kind}`);
  node.replaceChildren();
  node.insertAdjacentHTML(
    'afterbegin',
    `<p><span class="tag">${escapeHtml(label)}</span>${escapeHtml(message)}</p>${list}`,
  );
}

function download(blob, filename) {
  const link = document.createElement('a');
  link.setAttribute('href', URL.createObjectURL(blob));
  link.setAttribute('download', filename);
  link.click();
  URL.revokeObjectURL(link.getAttribute('href'));
}

function snapHitPoints(value) {
  if (value < HIGH_HP) return value;
  const floor = Math.floor(value / 1000) * 1000 + MARKER_REMAINDER;
  return floor <= value ? floor : floor - 1000;
}

function setUpTabs() {
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const select = (chosen) => {
    tabs.forEach((tab) => {
      const on = tab === chosen;
      tab.setAttribute('aria-selected', String(on));
      $(tab.getAttribute('aria-controls')).toggleAttribute('hidden', !on);
    });
  };
  tabs.forEach((tab) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', (event) => {
      const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
      if (!step) return;
      event.preventDefault();
      const next = tabs[(tabs.indexOf(tab) + step + tabs.length) % tabs.length];
      next.focus();
      select(next);
    });
  });
}

function setUpStats() {
  ['hp', 'st', 'df'].forEach((key) => {
    const input = $(key);
    const sync = () => {
      const snapped = key === 'hp' ? snapHitPoints(Number(input.value)) : Number(input.value);
      if (String(snapped) !== input.value) input.value = String(snapped);
      $(`${key}-out`).textContent = snapped.toLocaleString('en-US');
      if (key === 'hp') $('hp-note').toggleAttribute('hidden', snapped < HIGH_HP);
    };
    input.addEventListener('input', sync);
    sync();
  });
}

const optionsFor = (races) =>
  races
    .map((race) => `<option value="${race.name}">${escapeHtml(race.label)}</option>`)
    .join('');

async function setUpChoices() {
  const [races, abilities] = await Promise.all([
    getJson('/api/races'),
    getJson('/api/abilities'),
  ]);
  const fighters = races.filter((race) => race.is_fighter);

  $('race').insertAdjacentHTML('afterbegin', optionsFor(fighters));
  $('race').value = 'human';
  $('many-race').insertAdjacentHTML(
    'afterbegin',
    `<option value="">Any kind</option>${optionsFor(fighters)}`,
  );

  const hint = () => {
    const chosen = fighters.find((race) => race.name === $('race').value);
    $('race-hint').textContent = chosen ? chosen.description : '';
  };
  $('race').addEventListener('change', hint);
  hint();

  $('ability').insertAdjacentHTML(
    'afterbegin',
    abilities
      .filter((ability) => ability.usable_in_battle)
      .map(
        (ability) =>
          `<option value="${ability.code}">` +
          `${String(ability.code).padStart(2, '0')} ${escapeHtml(ability.description)}` +
          `</option>`,
      )
      .join(''),
  );
  $('ability').value = '0';
}

function oneCardPayload() {
  return {
    name: $('name').value || 'Card',
    hp: $('hp').value,
    st: $('st').value,
    df: $('df').value,
    race: $('race').value,
    ability: Number($('ability').value),
    nearest: $('nearest').checked,
    backRead: $('backRead').checked,
    ...($('class').value ? { class: $('class').value } : {}),
    ...($('speed').value !== '' ? { speed: Number($('speed').value) } : {}),
    ...($('job').value !== '' ? { job: Number($('job').value) } : {}),
  };
}

function describeResult(body) {
  if (body.is_exact) {
    setStatus('one-status', 'good', 'Exact', 'The machine will read exactly these numbers.');
  } else {
    setStatus(
      'one-status',
      'warn',
      'Closest',
      'Those exact numbers are impossible on this machine. This is the nearest card.',
      body.differences,
    );
  }
  $('one-code').toggleAttribute('hidden', false);
  $('one-code-value').textContent = body.barcode;
}

async function showPreview(barcode, name) {
  const { ok, response } = await postJson('/api/preview', { barcode, name });
  if (!ok) return;
  const image = $('card-image');
  const previous = image.getAttribute('src');
  image.setAttribute('src', URL.createObjectURL(await response.blob()));
  image.setAttribute('alt', `The card for ${name}, showing its stats and barcode`);
  if (previous) URL.revokeObjectURL(previous);
  $('card-placeholder').toggleAttribute('hidden', true);
}

async function makeOneCard(event) {
  event?.preventDefault();
  cheatCard = null;
  const button = $('one').querySelector('button[type="submit"]');
  button.toggleAttribute('disabled', true);
  try {
    const { ok, body } = await postJson('/api/generate', oneCardPayload());
    if (!ok) {
      setStatus('one-status', 'bad', 'Not possible', 'Try adjusting:', reasons(body));
      return null;
    }
    describeResult(body);
    await showPreview(body.barcode, $('name').value || 'Card');
    return body;
  } finally {
    button.toggleAttribute('disabled', false);
  }
}

async function downloadOneCard() {
  if (cheatCard) {
    const name = $('name').value.trim() || cheatCard.name;
    await downloadBarcodes([{ ...cheatCard, name }], 'cheat-card.pdf', 'one-status');
    return;
  }
  const result = await makeOneCard();
  if (!result) return;
  const { ok, body, response } = await postJson('/api/sheet', {
    cards: [{ ...oneCardPayload(), hp: String(result.character.hp) }],
  });
  if (!ok) {
    setStatus('one-status', 'bad', 'Not possible', 'Try adjusting:', reasons(body));
    return;
  }
  download(await response.blob(), 'card.pdf');
}

function sheetPayload() {
  const range = (key) => `${$(`${key}-min`).value}-${$(`${key}-max`).value}`;
  return {
    count: Number($('count').value),
    hp: range('hp'),
    st: range('st'),
    df: range('df'),
    ...($('seed').value !== '' ? { seed: Number($('seed').value) } : {}),
    ...($('many-race').value ? { race: $('many-race').value } : {}),
  };
}

async function makeSheet(event) {
  event?.preventDefault();
  const button = $('many').querySelector('button[type="submit"]');
  button.toggleAttribute('disabled', true);
  try {
    const { ok, body } = await postJson('/api/sheet-preview', sheetPayload());
    if (!ok) {
      setStatus('many-status', 'bad', 'Not possible', 'Try adjusting:', reasons(body));
      return false;
    }
    const frame = $('sheet-frame');
    frame.replaceChildren();
    frame.insertAdjacentHTML(
      'afterbegin',
      body.pages
        .map((page, index) => `<img src="${page}" alt="Page ${index + 1} of the sheet">`)
        .join(''),
    );
    const pages = body.pages.length;
    setStatus(
      'many-status',
      'good',
      'Ready',
      `${body.count} cards across ${pages} ${pages === 1 ? 'page' : 'pages'}.`,
    );
    return true;
  } finally {
    button.toggleAttribute('disabled', false);
  }
}

async function downloadSheet() {
  if (!(await makeSheet())) return;
  const { ok, body, response } = await postJson('/api/random', sheetPayload());
  if (!ok) {
    setStatus('many-status', 'bad', 'Not possible', 'Try adjusting:', reasons(body));
    return;
  }
  download(await response.blob(), 'cards.pdf');
}

async function downloadBarcodes(cards, filename, statusId) {
  const { ok, body, response } = await postJson('/api/barcode-sheet', { cards });
  if (!ok) {
    setStatus(statusId, 'bad', 'Not possible', 'Try again:', reasons(body));
    return;
  }
  download(await response.blob(), filename);
}

function showPages(frameId, pages, label) {
  const frame = $(frameId);
  frame.replaceChildren();
  frame.insertAdjacentHTML(
    'afterbegin',
    pages
      .map((page, index) => `<img src="${page}" alt="${escapeHtml(label)}, page ${index + 1}">`)
      .join(''),
  );
}

function officialPayload() {
  const chosen = $('official-set').value;
  return chosen ? { set: chosen } : {};
}

async function setUpOfficial() {
  const catalogue = await getJson('/api/official');
  const select = $('official-set');
  select.insertAdjacentHTML(
    'afterbegin',
    `<option value="">Every set, ${catalogue.total} cards</option>` +
      catalogue.sets
        .map(
          (entry) =>
            `<option value="${entry.key}" data-japanese="${escapeHtml(entry.japanese)}">` +
            `${escapeHtml(entry.english)}, ${entry.count} cards</option>`,
        )
        .join(''),
  );
  const hint = () => {
    const option = select.selectedOptions[0];
    $('official-hint').textContent = option?.dataset.japanese
      ? `In Japanese: ${option.dataset.japanese}`
      : 'Every card from every set, one after another.';
  };
  select.addEventListener('change', hint);
  hint();
  $('official-rejected').insertAdjacentHTML(
    'afterbegin',
    catalogue.rejected
      .map((entry) => `<li><code>${escapeHtml(entry.barcode)}</code> ${escapeHtml(entry.name)}</li>`)
      .join(''),
  );
}

async function showOfficial(event) {
  event?.preventDefault();
  const button = $('official').querySelector('button[type="submit"]');
  button.toggleAttribute('disabled', true);
  setStatus('official-status', 'info', 'Working', 'Drawing the cards...');
  try {
    const { ok, body } = await postJson('/api/official-preview', officialPayload());
    if (!ok) {
      setStatus('official-status', 'bad', 'Not possible', 'Try again:', reasons(body));
      return;
    }
    showPages('official-frame', body.pages, 'Official cards');
    const shown = body.pages.length * 9;
    const more = body.count > shown ? ` The first ${shown} are shown here; the download has all of them.` : '';
    setStatus('official-status', 'good', 'Ready', `${body.count} cards.${more}`);
  } finally {
    button.toggleAttribute('disabled', false);
  }
}

async function downloadOfficial() {
  setStatus('official-status', 'info', 'Working', 'Building the file. A big set takes a moment.');
  const { ok, body, response } = await postJson('/api/official-sheet', officialPayload());
  if (!ok) {
    setStatus('official-status', 'bad', 'Not possible', 'Try again:', reasons(body));
    return;
  }
  download(await response.blob(), 'official-cards.pdf');
  setStatus('official-status', 'good', 'Done', 'The file is in your downloads.');
}

function celebrate() {
  $('cheat-quip').textContent = pick(CHEAT_QUIPS);
  $('cheat-banner').toggleAttribute('hidden', false);
  document.body.classList.add('cheat-shake');
  setTimeout(() => document.body.classList.remove('cheat-shake'), SHAKE_MS);
}

async function activateCheat() {
  const field = $('name');
  const typed = field.value.trim();
  const custom = typed && typed !== field.defaultValue;
  const { ok, body } = await postJson('/api/cheat', custom ? { name: typed } : {});
  if (!ok) return;
  cheatCard = { barcode: body.barcode, name: body.name };
  field.value = body.name;
  $('race').value = body.character.race;
  $('race').dispatchEvent(new Event('change'));
  $('class').value = body.character.character_class ?? '';
  $('tab-one').click();
  celebrate();
  const { hp, st, df } = body.character;
  setStatus(
    'one-status',
    'cheat',
    'Cheat',
    `${body.name}: ${hp} health, ${st} attack, ${df} defence, and its attack doubles.`,
  );
  $('one-code').toggleAttribute('hidden', false);
  $('one-code-value').textContent = body.barcode;
  await showPreview(body.barcode, body.name);
}

async function setUpCheat() {
  const codes = new Set(await getJson('/api/cheat-codes'));
  $('cheat').addEventListener('submit', async (event) => {
    event.preventDefault();
    const typed = $('cheat-code').value.toUpperCase().replace(/\s+/g, '');
    if (codes.has(typed)) {
      $('cheat-reply').textContent = 'Oh no. You found it.';
      $('cheat-code').value = '';
      await activateCheat();
    } else {
      $('cheat-reply').textContent = pick(WRONG_CODE_REPLIES);
    }
  });

  let progress = 0;
  document.addEventListener('keydown', async (event) => {
    const typing = event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement;
    if (typing) return;
    const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
    progress = key === KONAMI[progress] ? progress + 1 : Number(key === KONAMI[0]);
    if (progress === KONAMI.length) {
      progress = 0;
      await activateCheat();
    }
  });
}

function copyCode() {
  navigator.clipboard?.writeText($('one-code-value').textContent);
  $('one-copy').textContent = 'Copied';
  setTimeout(() => {
    $('one-copy').textContent = 'Copy';
  }, 1500);
}

setUpTabs();
setUpStats();
$('one').addEventListener('submit', makeOneCard);
$('one-pdf').addEventListener('click', downloadOneCard);
$('one-copy').addEventListener('click', copyCode);
$('many').addEventListener('submit', makeSheet);
$('many-pdf').addEventListener('click', downloadSheet);
$('official').addEventListener('submit', showOfficial);
$('official-pdf').addEventListener('click', downloadOfficial);
setUpChoices();
setUpOfficial();
setUpCheat();
