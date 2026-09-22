const HIGH_HP = 20000;
const MARKER_REMAINDER = 900;
const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

const $ = (id) => document.getElementById(id);

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
setUpChoices();
