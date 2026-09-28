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

const $ = (id) => document.getElementById(id);

const pick = (items) => items[Math.floor(Math.random() * items.length)];

const escapeHtml = (text) => String(text).replace(/[&<>"']/g, (ch) => ESCAPES[ch]);

const isJapanese = () => currentLanguage === 'ja';


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
      tab.tabIndex = on ? 0 : -1;
      $(tab.getAttribute('aria-controls')).toggleAttribute('hidden', !on);
    });
    rememberTab(chosen);
  };
  select(tabFromHash() ?? tabs.find((tab) => tab.getAttribute('aria-selected') === 'true') ?? tabs[0]);
  window.addEventListener('hashchange', () => {
    const chosen = tabFromHash();
    if (chosen) select(chosen);
  });
  tabs.forEach((tab) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', (event) => {
      const ends = { Home: 0, End: tabs.length - 1 };
      const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
      if (!step && !(event.key in ends)) return;
      event.preventDefault();
      const next = step
        ? tabs[(tabs.indexOf(tab) + step + tabs.length) % tabs.length]
        : tabs[ends[event.key]];
      next.focus();
      select(next);
    });
  });
}

function setUpStats() {
  ['hp', 'st', 'df'].forEach((key) => {
    const sync = () => {
      const raw = Number($(key).value);
      const frontRead = isSecond() && !$('backRead').checked;
      const snapped = key === 'hp' && frontRead ? snapHitPoints(raw) : raw;
      if (snapped !== raw) $(key).value = String(snapped);
      $(`${key}-box`).value = String(snapped);
      if (key === 'hp') $('hp-note').toggleAttribute('hidden', !frontRead || snapped < HIGH_HP);
    };
    $(key).addEventListener('input', sync);
    $(`${key}-box`).addEventListener('change', () => {
      if (!showProblem($(`${key}-box`))) return;
      $(key).value = $(`${key}-box`).value;
      sync();
    });
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
    device: currentDevice(),
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
  if (!checkForm($('one'))) return null;
  cheatCard = null;
  const button = $('one').querySelector('button[type="submit"]');
  setBusy(button, true);
  try {
    if (!isSecond()) return await makeDeviceCard();
    const { ok, body } = await postJson('/api/generate', oneCardPayload());
    if (!ok) {
      refuse('one-status', body);
      return null;
    }
    describeResult(body);
    await showPreview(body.barcode, $('name').value || 'Card');
    return body;
  } finally {
    setBusy(button, false);
  }
}

function withCompanion(card) {
  const { companion, ...first } = card;
  return companion ? [first, { ...first, barcode: companion }] : [first];
}

async function downloadOneCard() {
  if (cheatCard) {
    const name = $('name').value.trim() || cheatCard.name;
    await downloadBarcodes(withCompanion({ ...cheatCard, name }), 'cheat-card.pdf', 'one-status');
    return;
  }
  const result = await makeOneCard();
  if (!result) return;
  if (!isSecond()) {
    const name = $('name').value.trim() || 'Card';
    const card = { barcode: result.barcode, name, device: currentDevice(), companion: result.companion };
    await downloadBarcodes(withCompanion(card), 'card.pdf', 'one-status');
    return;
  }
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
    hp: range('hp'),
    st: range('st'),
    df: range('df'),
    ...($('seed').value !== '' ? { seed: Number($('seed').value) } : {}),
    ...($('many-race').value && readsOnSheet('race') ? { race: $('many-race').value } : {}),
    device: currentDevice(),
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
  if (!checkForm($('many'))) return false;
  const button = $('many').querySelector('button[type="submit"]');
  setBusy(button, true);
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
    setBusy(button, false);
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
  });
  if (!ok) {
    refuse(statusId, body, 'status.again');
    return;
  }
  download(await response.blob(), filename);
}

function officialPayload() {
  const chosen = catalogue?.sets.length > 1 ? $('official-set').value : '';
  return { device: currentDevice(), ...(chosen ? { set: chosen } : {}) };
}

function renderOfficial() {
  if (!catalogue) return;
  renderOfficialSources();
  const none = catalogue.sets.length === 0;
  $('official-actions').toggleAttribute('hidden', none);
  $('official-sets').toggleAttribute('hidden', none);
  $('official-preview').toggleAttribute('hidden', none);
  $('panel-official').toggleAttribute('data-empty', none);
  const single = catalogue.sets.length === 1 ? catalogue.sets[0] : null;
  $('official-set-field').toggleAttribute('hidden', Boolean(single) || none);
  if (none) {
    $('official-single').toggleAttribute('hidden', true);
    return;
  }
  $('official-single').toggleAttribute('hidden', !single);
  if (single) {
    $('official-single').textContent = t('official.single', {
      title: isJapanese() ? single.japanese : single.english,
      count: single.count,
    });
    return;
  }
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

function renderOfficialSources() {
  const sources = [...document.querySelectorAll('[data-official-source]')]
    .map((node) => node.dataset.officialSource);
  const source = sources.includes(currentDevice()) ? currentDevice() : 'epoch';
  document.querySelectorAll('[data-official-source]').forEach((node) => {
    node.toggleAttribute('hidden', node.dataset.officialSource !== source);
  });
  const linked = document.querySelector(`.note-sources [data-official-source="${source}"]`);
  $('official-sources').toggleAttribute('hidden', !linked);
  $('official-sources').nextElementSibling.toggleAttribute('hidden', !linked);
  $('official-skipped').toggleAttribute('hidden', catalogue.rejected.length === 0);
  $('official-rejected').replaceChildren();
  $('official-rejected').insertAdjacentHTML(
    'afterbegin',
    catalogue.rejected
      .map((entry) => `<li><code>${escapeHtml(entry.barcode)}</code> ${escapeHtml(entry.name)}</li>`)
      .join(''),
  );
}

async function loadOfficial() {
  const device = currentDevice();
  const loaded = await getJson(`/api/official?device=${device}`);
  if (device !== currentDevice()) return;
  catalogue = loaded;
  renderOfficial();
  $('official-frame').replaceChildren();
  $('official-frame').insertAdjacentHTML(
    'afterbegin',
    `<p class="placeholder">${escapeHtml(t('official.placeholder'))}</p>`,
  );
  $('official-status').replaceChildren();
}

async function setUpOfficial() {
  $('official-set').addEventListener('change', showOfficialHint);
  await loadOfficial();
}

async function showOfficial(event) {
  event?.preventDefault();
  const button = $('official').querySelector('button[type="submit"]');
  setBusy(button, true);
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
    setBusy(button, false);
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
  if (!isSecond()) {
    await activateDeviceCheat(custom ? typed : '');
    return;
  }
  const { ok, body } = await postJson('/api/cheat', custom ? { name: typed } : {});
  if (!ok) return;
  cheatCard = { barcode: body.barcode, name: body.name, device: currentDevice() };
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

function setUpCheat() {
  $('konami').addEventListener('click', activateCheat);

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


function factRow(key, value) {
  return `<dt>${escapeHtml(t(key))}</dt><dd>${escapeHtml(String(value))}</dd>`;
}

function battleRows(character) {
  return [
    ['fact.battle_st', character.battle_st],
    ['fact.battle_df', character.battle_df],
  ].filter(([, value]) => value !== null).map(([key, value]) => factRow(key, value));
}

function showFacts(character) {
  const race = raceList.find((entry) => entry.name === character.race);
  const rows = [
    factRow('fact.kind', race ? raceName(race) : character.race),
    factRow('fact.hp', character.hp),
    factRow('fact.st', character.st),
    factRow('fact.df', character.df),
    ...battleRows(character),
    factRow('fact.power', `${String(character.special.code).padStart(2, '0')} ` +
      `${isJapanese() ? character.special.description_ja : character.special.description}`),
    factRow('fact.reading', t(`reading.${character.read_type}`)),
  ];
  if (character.character_class) {
    rows.splice(1, 0, factRow('fact.class', t(`class.${character.character_class}`)));
  }
  if (character.speed !== null) rows.push(factRow('fact.speed', character.speed));
  $('read-facts').replaceChildren();
  $('read-facts').insertAdjacentHTML('afterbegin', rows.join(''));
  $('read-facts').toggleAttribute('hidden', false);
}

const typedBarcode = () => $('read-barcode').value.replace(/\D/g, '');

const typedName = () => $('read-name').value.trim() || t('read.name.placeholder');

async function readBarcode(event) {
  event?.preventDefault();
  const barcode = typedBarcode();
  if (!barcode) {
    setStatus('read-status', 'bad', 'tag.impossible', t('read.empty'));
    return null;
  }
  const url = isSecond() ? `/api/decode/${barcode}` : `/api/read/${currentDevice()}/${barcode}`;
  const response = await fetch(url);
  const body = await response.json();
  if (!response.ok) {
    setStatus('read-status', 'bad', 'tag.impossible', t('read.refused'), reasons(body));
    $('read-facts').toggleAttribute('hidden', true);
    return null;
  }
  setStatus('read-status', 'good', 'tag.ready', t('read.ok'));
  if (isSecond()) {
    showFacts(body);
  } else {
    showDeviceFacts(body.facts);
  }
  await nameItFromShopping(barcode);
  await showReadPreview(barcode, typedName());
  return barcode;
}

async function nameItFromShopping(barcode) {
  if ($('read-name').value.trim()) return;
  try {
    const { name } = await getJson(`/api/lookup/${barcode}`);
    if (name) $('read-name').value = name;
  } catch {
    $('read-name').dataset.lookupFailed = 'true';
  }
}

async function showReadPreview(barcode, name) {
  const { ok, response } = await postJson('/api/preview', {
    barcode,
    name,
    device: currentDevice(),
  });
  if (!ok) return;
  const previous = $('read-image').getAttribute('src');
  $('read-image').setAttribute('src', URL.createObjectURL(await response.blob()));
  $('read-image').setAttribute('alt', t('alt.card', { name }));
  if (previous) URL.revokeObjectURL(previous);
  $('read-placeholder').toggleAttribute('hidden', true);
}

let shelf = [];

function resetShelf() {
  shelf = [];
  $('shop-list').replaceChildren();
  $('shop-placeholder').toggleAttribute('hidden', false);
  $('shop-status').replaceChildren();
}

function shelfRow(product) {
  const name = isJapanese() ? product.label_ja : product.label;
  return [
    '<li class="shelf-row">',
    `<span class="shelf-name" lang="ja">${escapeHtml(product.name)}</span>`,
    `<span class="shelf-kind">${escapeHtml(name)}</span>`,
    `<span class="shelf-stats">${escapeHtml(isJapanese() ? product.stats_ja : product.stats)}</span>`,
    product.note
      ? `<span class="shelf-note">${escapeHtml(isJapanese() ? product.note_ja : product.note)}</span>`
      : '',
    `<code class="shelf-code">${escapeHtml(product.barcode)}</code>`,
    '</li>',
  ].join('');
}

function showShelf(body) {
  shelf = body.products;
  $('shop-list').innerHTML = shelf.map(shelfRow).join('');
  $('shop-placeholder').toggleAttribute('hidden', shelf.length > 0);
  $('shop-credit').textContent = t('shop.credit', body);
  if (!shelf.length) {
    setStatus('shop-status', 'bad', 'tag.impossible', t('shop.empty'));
    return;
  }
  setStatus('shop-status', 'good', 'tag.ready',
    t('shop.found', { count: shelf.length, total: body.total }));
}

async function searchShelf(event) {
  event?.preventDefault();
  const query = encodeURIComponent($('shop-query').value.trim());
  showShelf(await getJson(`/api/products?q=${query}&device=${currentDevice()}`));
}

async function surpriseShelf() {
  const body = await getJson(`/api/products?q=&device=${currentDevice()}`);
  const pool = [...body.products];
  const picked = [];
  while (picked.length < CARDS_PER_PAGE && pool.length) {
    picked.push(...pool.splice(Math.floor(Math.random() * pool.length), 1));
  }
  $('shop-query').value = '';
  showShelf({ ...body, products: picked });
}

async function downloadShelf() {
  if (!shelf.length) {
    setStatus('shop-status', 'bad', 'tag.impossible', t('shop.empty'));
    return;
  }
  const device = currentDevice();
  const cards = shelf
    .filter((product) => product.readable)
    .map(({ barcode, name }) => ({ barcode, name, device }));
  await downloadBarcodes(cards, 'supermarket.pdf', 'shop-status');
}

async function downloadRead() {
  const barcode = await readBarcode();
  if (!barcode) return;
  await downloadBarcodes([{ barcode, name: typedName(), device: currentDevice() }],
    'card.pdf', 'read-status');
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
    renderDevices();
  });
  applyLanguage(currentLanguage);
}

setUpValidation();
setUpTabs();
setUpStats();
setUpLanguage();
$('one').addEventListener('submit', makeOneCard);
$('one-pdf').addEventListener('click', downloadOneCard);
$('one-copy').addEventListener('click', copyCode);
$('many').addEventListener('submit', makeSheet);
$('many-pdf').addEventListener('click', downloadSheet);
$('official').addEventListener('submit', showOfficial);
$('read').addEventListener('submit', readBarcode);
$('read-pdf').addEventListener('click', downloadRead);
$('shop').addEventListener('submit', searchShelf);
setUpSearchAsYouType($('shop-query'), searchShelf);
$('shop-surprise').addEventListener('click', surpriseShelf);
$('shop-pdf').addEventListener('click', downloadShelf);
$('official-pdf').addEventListener('click', downloadOfficial);
setUpLivePreview();
setUpOfficial();
Promise.all([setUpChoices(), setUpDevices()])
  .then(refreshPreviewSoon)
  .catch(() => setStatus('one-status', 'bad', 'tag.impossible', t('status.wrong')));
setUpCheat();
