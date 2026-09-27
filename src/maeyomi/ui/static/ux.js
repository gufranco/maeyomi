const SEARCH_DELAY_MS = 250;
const TAB_PREFIX = 'tab-';

function setBusy(button, busy) {
  button.toggleAttribute('disabled', busy);
  button.setAttribute('aria-busy', String(busy));
}

function tabFromHash() {
  const name = decodeURIComponent(window.location.hash.slice(1));
  return name ? document.getElementById(TAB_PREFIX + name) : null;
}

function rememberTab(tab) {
  const name = tab.id.slice(TAB_PREFIX.length);
  if (window.location.hash.slice(1) !== name) {
    window.history.replaceState(null, '', `#${name}`);
  }
}

function problemFor(input) {
  const validity = input.validity;
  const limits = { min: input.getAttribute('min'), max: input.getAttribute('max') };
  if (validity.badInput) return t('valid.number');
  if (validity.rangeUnderflow || validity.rangeOverflow) return t('valid.range', limits);
  if (validity.stepMismatch) return t('valid.step', { step: input.getAttribute('step') });
  return '';
}

function problemNodeFor(input) {
  const id = `${input.id}-problem`;
  const existing = document.getElementById(id);
  if (existing) return existing;
  input.insertAdjacentHTML('afterend', `<span class="field-problem" id="${id}" role="alert"></span>`);
  const described = input.getAttribute('aria-describedby');
  input.setAttribute('aria-describedby', described ? `${described} ${id}` : id);
  return document.getElementById(id);
}

function showProblem(input) {
  const problem = problemFor(input);
  input.setAttribute('aria-invalid', String(Boolean(problem)));
  input.closest('.field')?.classList.toggle('invalid', Boolean(problem));
  problemNodeFor(input).textContent = problem;
  return !problem;
}

function checkForm(form) {
  const inputs = [...form.querySelectorAll('input[type="number"][id]')];
  const failing = inputs.filter((input) => !showProblem(input));
  failing[0]?.focus();
  return failing.length === 0;
}

function setUpValidation() {
  document.querySelectorAll('form').forEach((form) => {
    form.setAttribute('novalidate', '');
    form.querySelectorAll('input[type="number"][id]').forEach((input) => {
      input.addEventListener('input', () => showProblem(input));
    });
    form.addEventListener('submit', (event) => {
      if (checkForm(form)) return;
      event.preventDefault();
      event.stopImmediatePropagation();
    }, true);
  });
}

function setUpSearchAsYouType(input, search) {
  let pending = null;
  input.addEventListener('input', () => {
    clearTimeout(pending);
    pending = setTimeout(() => {
      search().catch(() => setStatus('shop-status', 'bad', 'tag.impossible', t('status.wrong')));
    }, SEARCH_DELAY_MS);
  });
}
