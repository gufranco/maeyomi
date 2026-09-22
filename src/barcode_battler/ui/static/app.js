const HIGH_HP = 20000;
const MARKER_REMAINDER = 900;
const CARDS_PER_PAGE = 9;
const COPY_RESET_MS = 1500;
const SHAKE_MS = 700;
const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const KONAMI = [
  'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
  'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a',
];

let raceList = [];
let abilityList = [];
let catalogue = null;
let cheatCard = null;
let wrongCount = 0;

const $ = (id) => document.getElementById(id);

const pick = (items) => items[Math.floor(Math.random() * items.length)];

const escapeHtml = (text) => String(text).replace(/[&<>"']/g, (ch) => ESCAPES[ch]);

const isJapanese = () => currentLanguage === 'ja';

const orientation = () => $('orientation').value;

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
  return [t('status.wrong')];
}

function setStatus(id, kind, tagKey, message, items = []) {
  const list = items.length
    ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`
    : '';
  const node = $(id);
  node.setAttribute('class', `status is-${kind}`);
  node.replaceChildren();
  node.insertAdjacentHTML(
    'afterbegin',
    `<p><span class="tag">${escapeHtml(t(tagKey))}</span>${escapeHtml(message)}</p>${list}`,
  );
}

const refuse = (id, body, key = 'status.adjust') =>
  setStatus(id, 'bad', 'tag.impossible', t(key), reasons(body));

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
    const sync = () => {
      const raw = Number($(key).value);
      const snapped = key === 'hp' ? snapHitPoints(raw) : raw;
      if (snapped !== raw) $(key).value = String(snapped);
      $(`${key}-out`).textContent = snapped.toLocaleString('en-US');
      if (key === 'hp') $('hp-note').toggleAttribute('hidden', snapped < HIGH_HP);
    };
    $(key).addEventListener('input', sync);
    sync();
  });
}

const optionHtml = (value, label, chosen) =>
  `<option value="${escapeHtml(value)}"${value === chosen ? ' selected' : ''}>` +
  `${escapeHtml(label)}</option>`;

function fillSelect(id, options, fallback) {
  const current = $(id).value || fallback;
  const chosen = options.some((option) => option.value === current) ? current : fallback;
  $(id).replaceChildren();
  $(id).insertAdjacentHTML(
    'afterbegin',
    options.map((option) => optionHtml(option.value, option.label, chosen)).join(''),
  );
}

const raceName = (race) => (isJapanese() ? race.label_ja : race.label);
const raceHint = (race) => (isJapanese() ? race.description_ja : race.description);
const abilityText = (ability) => (isJapanese() ? ability.description_ja : ability.description);

function renderChoices() {
  const fighters = raceList
    .filter((race) => race.is_fighter)
    .map((race) => ({ value: race.name, label: raceName(race) }));
  fillSelect('race', fighters, 'human');
  fillSelect('many-race', [{ value: '', label: t('many.anyRace') }, ...fighters], '');
  fillSelect(
    'ability',
    abilityList
      .filter((ability) => ability.usable_in_battle)
      .map((ability) => ({
        value: String(ability.code),
        label: `${String(ability.code).padStart(2, '0')} ${abilityText(ability)}`,
      })),
    '0',
  );
  showRaceHint();
}

function showRaceHint() {
  const chosen = raceList.find((race) => race.name === $('race').value);
  $('race-hint').textContent = chosen ? raceHint(chosen) : '';
}

async function setUpChoices() {
  const [races, abilities] = await Promise.all([
    getJson('/api/races'),
    getJson('/api/abilities'),
  ]);
  raceList = races;
  abilityList = abilities;
  renderChoices();
  $('race').addEventListener('change', showRaceHint);
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
    orientation: orientation(),
    ...($('class').value ? { class: $('class').value } : {}),
    ...($('speed').value !== '' ? { speed: Number($('speed').value) } : {}),
    ...($('job').value !== '' ? { job: Number($('job').value) } : {}),
  };
}

function describeResult(body) {
  if (body.is_exact) {
    setStatus('one-status', 'good', 'tag.exact', t('status.exact'));
  } else {
    setStatus('one-status', 'warn', 'tag.closest', t('status.closest'), body.differences);
  }
  $('one-code').toggleAttribute('hidden', false);
  $('one-code-value').textContent = body.barcode;
}

async function showPreview(barcode, name) {
  const { ok, response } = await postJson('/api/preview', {
    barcode,
    name,
    orientation: orientation(),
  });
  if (!ok) return;
  const previous = $('card-image').getAttribute('src');
  $('card-image').setAttribute('src', URL.createObjectURL(await response.blob()));
  $('card-image').setAttribute('alt', t('alt.card', { name }));
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
      refuse('one-status', body);
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
    refuse('one-status', body);
    return;
  }
  download(await response.blob(), 'card.pdf');
}

function sheetPayload() {
  const range = (key) => `${$(`${key}-min`).value}-${$(`${key}-max`).value}`;
  return {
    count: Number($('count').value),
    orientation: orientation(),
    hp: range('hp'),
    st: range('st'),
    df: range('df'),
    ...($('seed').value !== '' ? { seed: Number($('seed').value) } : {}),
    ...($('many-race').value ? { race: $('many-race').value } : {}),
  };
}

function showPages(frameId, pages, label) {
  $(frameId).replaceChildren();
  $(frameId).insertAdjacentHTML(
    'afterbegin',
    pages
      .map(
        (page, index) =>
          `<img src="${page}" alt="${escapeHtml(t('alt.page', { label, page: index + 1 }))}">`,
      )
      .join(''),
  );
}

async function makeSheet(event) {
  event?.preventDefault();
  const button = $('many').querySelector('button[type="submit"]');
  button.toggleAttribute('disabled', true);
  try {
    const { ok, body } = await postJson('/api/sheet-preview', sheetPayload());
    if (!ok) {
      refuse('many-status', body);
      return false;
    }
    showPages('sheet-frame', body.pages, t('label.sheet'));
    const pages = body.pages.length;
    const message =
      pages === 1
        ? t('status.sheetOne', { count: body.count })
        : t('status.sheet', { count: body.count, pages });
    setStatus('many-status', 'good', 'tag.ready', message);
    return true;
  } finally {
    button.toggleAttribute('disabled', false);
  }
}

async function downloadSheet() {
  if (!(await makeSheet())) return;
  const { ok, body, response } = await postJson('/api/random', sheetPayload());
  if (!ok) {
    refuse('many-status', body);
    return;
  }
  download(await response.blob(), 'cards.pdf');
}

async function downloadBarcodes(cards, filename, statusId) {
  const { ok, body, response } = await postJson('/api/barcode-sheet', {
    cards,
    orientation: orientation(),
  });
  if (!ok) {
    refuse(statusId, body, 'status.again');
    return;
  }
  download(await response.blob(), filename);
}

function officialPayload() {
  const chosen = $('official-set').value;
  return chosen ? { set: chosen, orientation: orientation() } : { orientation: orientation() };
}

function renderOfficial() {
  if (!catalogue) return;
  const sets = catalogue.sets.map((entry) => ({
    value: entry.key,
    label: t('official.option', {
      title: isJapanese() ? entry.japanese : entry.english,
      count: entry.count,
    }),
  }));
  fillSelect(
    'official-set',
    [{ value: '', label: t('official.every', { count: catalogue.total }) }, ...sets],
    '',
  );
  showOfficialHint();
}

function showOfficialHint() {
  const entry = catalogue?.sets.find((set) => set.key === $('official-set').value);
  if (!entry) {
    $('official-hint').textContent = t('official.everyHint');
    return;
  }
  const other = isJapanese() ? entry.english : entry.japanese;
  $('official-hint').textContent = t('official.inJapanese', { title: other });
}

async function setUpOfficial() {
  catalogue = await getJson('/api/official');
  renderOfficial();
  $('official-set').addEventListener('change', showOfficialHint);
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
  setStatus('official-status', 'info', 'tag.working', t('status.drawing'));
  try {
    const { ok, body } = await postJson('/api/official-preview', officialPayload());
    if (!ok) {
      refuse('official-status', body, 'status.again');
      return;
    }
    showPages('official-frame', body.pages, t('label.official'));
    const shown = body.pages.length * CARDS_PER_PAGE;
    const message =
      body.count > shown
        ? t('status.officialMore', { count: body.count, shown })
        : t('status.official', { count: body.count });
    setStatus('official-status', 'good', 'tag.ready', message);
  } finally {
    button.toggleAttribute('disabled', false);
  }
}

async function downloadOfficial() {
  setStatus('official-status', 'info', 'tag.working', t('status.building'));
  const { ok, body, response } = await postJson('/api/official-sheet', officialPayload());
  if (!ok) {
    refuse('official-status', body, 'status.again');
    return;
  }
  download(await response.blob(), 'official-cards.pdf');
  setStatus('official-status', 'good', 'tag.done', t('status.saved'));
}

function celebrate() {
  $('cheat-quip').textContent = pick(t('quips'));
  $('cheat-banner').toggleAttribute('hidden', false);
  document.body.classList.add('cheat-shake');
  setTimeout(() => document.body.classList.remove('cheat-shake'), SHAKE_MS);
}

async function activateCheat() {
  const typed = $('name').value.trim();
  const custom = typed && typed !== $('name').defaultValue;
  const { ok, body } = await postJson('/api/cheat', custom ? { name: typed } : {});
  if (!ok) return;
  cheatCard = { barcode: body.barcode, name: body.name };
  $('name').value = body.name;
  $('race').value = body.character.race;
  showRaceHint();
  $('class').value = body.character.character_class ?? '';
  $('tab-one').click();
  celebrate();
  const { hp, st, df } = body.character;
  setStatus('one-status', 'cheat', 'tag.cheat', t('status.cheat', { name: body.name, hp, st, df }));
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
      wrongCount = 0;
      $('cheat-reply').textContent = t('cheat.found');
      $('cheat-code').value = '';
      await activateCheat();
    } else {
      $('cheat-reply').textContent = warmerHint();
    }
  });

  $('cheat-code').addEventListener('focus', rotateRiddle);

  let progress = 0;
  document.addEventListener('keydown', async (event) => {
    const typing =
      event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement;
    if (typing) return;
    const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
    progress = key === KONAMI[progress] ? progress + 1 : Number(key === KONAMI[0]);
    if (progress === KONAMI.length) {
      progress = 0;
      await activateCheat();
    }
  });
}

function warmerHint() {
  const hints = t('hints');
  const reply = wrongCount === 0 ? pick(t('wrong')) : hints[Math.min(wrongCount - 1, hints.length - 1)];
  wrongCount += 1;
  return reply;
}

function rotateRiddle() {
  const riddles = t('riddles');
  $('cheat-code').setAttribute('placeholder', pick(riddles));
}

function copyCode() {
  navigator.clipboard?.writeText($('one-code-value').textContent);
  $('one-copy').textContent = t('copied');
  setTimeout(() => {
    $('one-copy').textContent = t('copy');
  }, COPY_RESET_MS);
}

function setUpLanguage() {
  document.querySelectorAll('[data-language]').forEach((button) => {
    button.addEventListener('click', () => applyLanguage(button.dataset.language));
  });
  document.addEventListener('languagechange', () => {
    renderChoices();
    renderOfficial();
  });
  applyLanguage(currentLanguage);
}

setUpTabs();
setUpStats();
$('orientation').addEventListener('change', () => {
  if (cheatCard) showPreview(cheatCard.barcode, $('name').value || cheatCard.name);
});
setUpLanguage();
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
