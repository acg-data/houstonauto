(() => {
  const C = window.HAP_CONFIG || {};
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const placeholders = !!C.showPlaceholders;
  const siteUrl = (C.siteUrl || location.origin).replace(/\/$/, '');
  document.documentElement.classList.toggle('show-placeholders', placeholders);

  /* ---------- Analytics ---------- */
  window.dataLayer = window.dataLayer || [];
  const gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  const googleIds = [C.ga4Id, (C.googleAdsConversion || '').split('/')[0]].filter(Boolean);
  if (googleIds.length) {
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(googleIds[0]);
    document.head.append(s);
    window.gtag = gtag;
    gtag('js', new Date());
    googleIds.forEach(id => gtag('config', id));
  }
  if (C.metaPixelId && !window.fbq) {
    const f = window.fbq = function () { f.callMethod ? f.callMethod.apply(f, arguments) : f.queue.push(arguments); };
    f.push = f; f.loaded = true; f.version = '2.0'; f.queue = [];
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://connect.facebook.net/en_US/fbevents.js';
    document.head.append(s);
    window.fbq('init', C.metaPixelId);
    window.fbq('track', 'PageView');
  }
  const metaEvents = { generate_lead: 'Lead', call_click: 'Contact', text_click: 'Contact', email_click: 'Contact' };
  function track(event, params = {}) {
    window.dataLayer.push({ event, ...params });
    if (googleIds.length) gtag('event', event, params);
    if (event === 'generate_lead' && C.googleAdsConversion) gtag('event', 'conversion', { send_to: C.googleAdsConversion });
    if (window.fbq) metaEvents[event] ? window.fbq('track', metaEvents[event]) : window.fbq('trackCustom', event, params);
  }

  /* Remember where this visit came from so requests carry ad attribution. */
  const ATTR_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid', 'fbclid', 'msclkid'];
  let attribution = {};
  try { attribution = JSON.parse(sessionStorage.getItem('hap_attribution') || '{}'); } catch {}
  const query = new URLSearchParams(location.search);
  if (!attribution.landing_page || ATTR_KEYS.some(k => query.has(k))) {
    attribution = { landing_page: location.pathname, referrer: document.referrer || '' };
    ATTR_KEYS.forEach(k => { if (query.get(k)) attribution[k] = query.get(k); });
    try { sessionStorage.setItem('hap_attribution', JSON.stringify(attribution)); } catch {}
  }

  /* ---------- Business details (config.js) ---------- */
  const DAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
  const ORDER = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
  const SHORT = { Mo: 'Mon', Tu: 'Tue', We: 'Wed', Th: 'Thu', Fr: 'Fri', Sa: 'Sat', Su: 'Sun' };
  const LONG = { Mo: 'Monday', Tu: 'Tuesday', We: 'Wednesday', Th: 'Thursday', Fr: 'Friday', Sa: 'Saturday', Su: 'Sunday' };

  const phone = (C.phone || '').trim();
  const phoneLabel = C.phoneDisplay || formatPhone(phone);
  const textNumber = (C.textNumber || '').trim();
  const email = (C.email || '').trim();
  const addr = C.address || {};
  const addressLines = addr.street ? [addr.street, [addr.city, [addr.region, addr.postalCode].filter(Boolean).join(' ')].filter(Boolean).join(', ')] : [];
  const mapsUrl = C.mapsUrl || (addressLines.length ? 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(['Houston Auto Pros', ...addressLines].join(', ')) : '');
  const hours = (C.hours || []).filter(h => h && Array.isArray(h.days) && /^\d\d:\d\d$/.test(h.opens) && /^\d\d:\d\d$/.test(h.closes));
  const rating = C.rating && C.rating.value ? C.rating : null;
  const reviews = (C.reviews || []).filter(r => r && r.quote);

  const available = {
    visit: addressLines.length > 0 || !!phone || !!email,
    phone: !!phone,
    text: !!textNumber,
    email: !!email,
    address: addressLines.length > 0,
    directions: !!mapsUrl,
    hours: hours.length > 0,
    rating: !!rating,
    reviews: reviews.length > 0 || !!C.reviewsUrl,
    reviewsUrl: !!C.reviewsUrl,
  };

  function formatPhone(p) {
    const d = p.replace(/\D/g, '').replace(/^1(?=\d{10}$)/, '');
    return d.length === 10 ? `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}` : p;
  }
  function formatTime(t) {
    const [h, m] = t.split(':').map(Number);
    return `${h % 12 || 12}${m ? ':' + String(m).padStart(2, '0') : ''} ${h < 12 ? 'AM' : 'PM'}`;
  }
  function houstonNow() {
    const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: 'America/Chicago', weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' })
      .formatToParts(new Date()).map(p => [p.type, p.value]));
    return { day: parts.weekday.slice(0, 2), minutes: Number(parts.hour) * 60 + Number(parts.minute) };
  }
  const toMinutes = t => { const [h, m] = t.split(':').map(Number); return h * 60 + m; };
  const hoursFor = day => hours.find(h => h.days.includes(day));
  function dayRange(days) {
    const idx = days.map(d => ORDER.indexOf(d)).sort((a, b) => a - b);
    const consecutive = idx.every((v, i) => i === 0 || v === idx[i - 1] + 1);
    if (idx.length > 2 && consecutive) return `${SHORT[ORDER[idx[0]]]}–${SHORT[ORDER[idx[idx.length - 1]]]}`;
    return idx.map(i => SHORT[ORDER[i]]).join(', ');
  }
  function todayStatus() {
    const now = houstonNow();
    const today = hoursFor(now.day);
    if (today && now.minutes < toMinutes(today.closes)) {
      return now.minutes >= toMinutes(today.opens) ? `Open today until ${formatTime(today.closes)}` : `Opens today at ${formatTime(today.opens)}`;
    }
    for (let i = 1; i <= 7; i++) {
      const day = DAYS[(DAYS.indexOf(now.day) + i) % 7];
      const h = hoursFor(day);
      if (h) return `Closed now · opens ${i === 1 ? 'tomorrow' : SHORT[day]} ${formatTime(h.opens)}`;
    }
    return '';
  }
  function renderHours(el) {
    const today = houstonNow().day;
    const rows = hours.map(h => ({ label: dayRange(h.days), value: `${formatTime(h.opens)} – ${formatTime(h.closes)}`, today: h.days.includes(today) }));
    const closed = ORDER.filter(d => !hoursFor(d));
    if (closed.length) rows.push({ label: dayRange(closed), value: 'Closed', today: closed.includes(today) });
    el.replaceChildren(...rows.map(r => {
      const li = document.createElement('li');
      li.className = r.today ? 'is-today' : '';
      li.append(Object.assign(document.createElement('span'), { textContent: r.label }), Object.assign(document.createElement('span'), { textContent: r.value }));
      return li;
    }));
  }

  const fills = {
    phone: () => phoneLabel,
    email: () => email,
    address: el => { el.replaceChildren(...addressLines.flatMap((l, i) => (i ? [document.createElement('br'), l] : [l]))); return true; },
    hours: el => { renderHours(el); return true; },
    today: () => todayStatus(),
    rating: () => rating && `★ ${rating.value}${rating.count ? ` · ${rating.count} Google reviews` : ' on Google'}`,
  };
  const placeholderText = { phone: 'Phone number', email: 'Email address', address: 'Street address', hours: 'Opening hours', today: 'Hours', rating: 'Google rating' };
  const placeholderKey = { today: 'hours' };

  $$('[data-requires]').forEach(el => {
    if (el.dataset.requires.split(' ').every(k => available[k])) return;
    if (placeholders) { el.classList.add('is-placeholder'); el.title = 'Add this detail in config.js'; }
    else el.hidden = true;
  });
  $$('[data-biz]').forEach(el => {
    const key = el.dataset.biz;
    const value = available[placeholderKey[key] || key] ? fills[key](el) : '';
    if (value === true) return;
    if (value) { el.textContent = value; return; }
    if (!placeholders) return;
    const text = el.dataset.placeholder || placeholderText[key];
    if (el.tagName === 'UL') el.replaceChildren(Object.assign(document.createElement('li'), { textContent: text }));
    else el.textContent = text;
    el.classList.add('is-placeholder');
  });

  const hrefs = {
    call: phone && 'tel:' + phone,
    text: textNumber && 'sms:' + textNumber,
    email: email && 'mailto:' + email,
    directions: mapsUrl,
    reviews: C.reviewsUrl,
  };
  $$('[data-action]').forEach(el => {
    const action = el.dataset.action;
    if (!hrefs[action]) return;
    el.href = hrefs[action];
    if (action === 'directions' || action === 'reviews') { el.target = '_blank'; el.rel = 'noopener'; }
    el.addEventListener('click', () => track(action + '_click', { location: el.dataset.source || '' }));
  });

  $$('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });

  if (!C.requestEndpoint && !C.schedulerUrl) {
    $$('[data-booking-faq]').forEach(faq => {
      $('summary', faq).firstChild.textContent = 'Can I book through this preview?';
      $('p', faq).textContent = 'You can put together a service brief and download a copy. Online booking is not connected in this preview, so nothing is sent to the shop and no appointment is reserved.';
    });
  }

  /* Structured data for local search. Only verified fields from config.js are included. */
  const business = {
    '@context': 'https://schema.org',
    '@type': 'AutoRepair',
    '@id': siteUrl + '/#business',
    name: 'Houston Auto Pros',
    url: siteUrl + '/',
    image: siteUrl + '/assets/og-image.jpg',
    logo: siteUrl + '/assets/logo-512.png',
    description: 'Independent European automotive service and repair in Houston for Porsche, BMW and Mercedes-Benz owners.',
    areaServed: { '@type': 'City', name: 'Houston' },
  };
  if (phone) business.telephone = phone;
  if (email) business.email = email;
  if (addressLines.length) business.address = { '@type': 'PostalAddress', streetAddress: addr.street, addressLocality: addr.city, addressRegion: addr.region, postalCode: addr.postalCode, addressCountry: 'US' };
  if (C.geo && C.geo.lat) business.geo = { '@type': 'GeoCoordinates', latitude: C.geo.lat, longitude: C.geo.lng };
  if (mapsUrl) business.hasMap = mapsUrl;
  if (hours.length) business.openingHoursSpecification = hours.map(h => ({ '@type': 'OpeningHoursSpecification', dayOfWeek: h.days.map(d => LONG[d]), opens: h.opens, closes: h.closes }));
  if ((C.sameAs || []).length) business.sameAs = C.sameAs;
  const ld = document.createElement('script');
  ld.type = 'application/ld+json';
  ld.textContent = JSON.stringify(business);
  if (C.launchState === 'production') document.head.append(ld);

  /* ---------- Reviews (real ones from config.js only) ---------- */
  const reviewsWrap = $('[data-reviews]');
  if (reviewsWrap) {
    const card = (quote, name, meta, isPlaceholder) => {
      const fig = document.createElement('figure');
      fig.className = 'review' + (isPlaceholder ? ' is-placeholder' : '');
      const q = document.createElement('blockquote');
      q.textContent = isPlaceholder ? quote : `“${quote}”`;
      const cap = document.createElement('figcaption');
      cap.append(Object.assign(document.createElement('b'), { textContent: name }), Object.assign(document.createElement('span'), { textContent: meta }));
      fig.append(q, cap);
      return fig;
    };
    if (reviews.length) {
      reviewsWrap.replaceChildren(...reviews.slice(0, 6).map(r => card(r.quote, r.name || 'Customer', [r.car, r.source || 'Google'].filter(Boolean).join(' · '))));
    } else if (placeholders) {
      reviewsWrap.replaceChildren(...[1, 2, 3].map(n => card('Paste a real review from your Google Business Profile into config.js. Copy it word for word, with the reviewer’s name as shown.', `Review ${n}`, 'config.js → reviews', true)));
    } else if (!C.reviewsUrl) {
      reviewsWrap.closest('section').hidden = true;
    } else {
      reviewsWrap.hidden = true;
    }
  }

  /* ---------- Photo slots ---------- */
  $$('.slot').forEach(fig => {
    const img = $('img', fig);
    if (!img) return;
    const path = img.getAttribute('src');
    if (placeholders) {
      const hint = document.createElement('div');
      hint.className = 'slot-hint';
      hint.setAttribute('aria-hidden', 'true');
      const label = Object.assign(document.createElement('b'), { textContent: 'Photo slot' });
      const file = Object.assign(document.createElement('code'), { textContent: 'dist' + path });
      hint.append(label, file);
      if (fig.dataset.hint) hint.append(document.createElement('br'), fig.dataset.hint);
      fig.append(hint);
    }
    const fail = () => {
      if (img.dataset.fallback && !fig.classList.contains('slot--fallback')) {
        fig.classList.add('slot--fallback');
        img.src = img.dataset.fallback;
        return;
      }
      fig.classList.remove('slot--fallback');
      fig.classList.add('slot--empty');
    };
    img.addEventListener('error', fail);
    if (img.complete && img.naturalWidth === 0) {
      // A lazy image may simply not have started; re-request it so any error fires with the listener attached.
      if (img.loading === 'lazy') img.src = path;
      else fail();
    }
  });

  /* ---------- Header ---------- */
  const header = $('[data-header]');
  const onScroll = () => header && header.classList.toggle('is-solid', window.scrollY > 24);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  const menu = $('.menu');
  const nav = $('#site-nav');
  function setMenu(open) {
    nav.classList.toggle('open', open);
    header.classList.toggle('menu-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.style.overflow = open ? 'hidden' : '';
  }
  if (menu && nav) {
    menu.addEventListener('click', () => setMenu(!nav.classList.contains('open')));
    nav.addEventListener('click', e => { if (e.target.closest('a, button')) setMenu(false); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); menu.focus(); } });
    window.matchMedia('(min-width: 861px)').addEventListener('change', e => { if (e.matches) setMenu(false); });
  }

  /* ---------- Appointment request ---------- */
  const dialog = $('#booking');
  const form = $('#request-form');
  if (dialog && form) {
    const steps = $$('.step', form);
    const nextBtn = $('[data-next]', form);
    const nextLabel = $('[data-label]', nextBtn);
    const backBtn = $('[data-back]', form);
    const bar = $('.progress span', form);
    const count = $('.step-count', form);
    const note = $('[data-form-note]', form);
    const result = $('#request-result', form);
    const flow = $$('.progress, .step-count, .step-actions, [data-form-note]', form);
    let step = 1;
    let returnFocus;
    let source = '';
    let sent = false;
    let requestUrl;

    if (!C.requestEndpoint) {
      $('h2', steps[2]).textContent = 'Your details for the visit.';
      form.elements.name.required = false;
      form.elements.phone.required = false;
    }

    note.textContent = C.requestEndpoint
      ? 'A request isn’t a confirmed booking. The shop will contact you to confirm a time.'
      : 'Preview mode: create and download a service brief. Nothing is sent to the shop. Your details stay in this browser unless you choose to share them.';

    const dateInput = form.elements.date;
    dateInput.min = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Chicago' }).format(new Date());
    dateInput.addEventListener('input', () => {
      dateInput.setCustomValidity('');
      if (!hours.length || !dateInput.value) return;
      const day = DAYS[new Date(dateInput.value + 'T12:00:00Z').getUTCDay()];
      if (!hoursFor(day)) dateInput.setCustomValidity(`The shop is closed on ${LONG[day]}s. Please choose another day.`);
    });

    const emailInput = form.elements.email;
    const emailOptional = $('[data-email-optional]', form);
    const syncEmail = () => {
      const needEmail = form.elements.contact.value === 'Email';
      emailInput.required = needEmail;
      emailOptional.hidden = needEmail;
    };
    form.addEventListener('change', e => { if (e.target.name === 'contact') syncEmail(); });

    function showStep(n) {
      step = n;
      steps.forEach((s, i) => { s.hidden = i !== n - 1; });
      flow.forEach(el => { el.hidden = false; });
      result.hidden = true;
      bar.style.transform = `scaleX(${n / steps.length})`;
      count.textContent = `Step ${n} of ${steps.length}`;
      backBtn.hidden = n === 1;
      setNextLabel();
    }
    function setNextLabel() {
      nextLabel.textContent = step < steps.length ? 'Continue' : (C.requestEndpoint ? 'Send request' : 'Create service brief');
    }
    function focusStep() {
      const heading = $('h2', steps[step - 1]);
      heading.setAttribute('tabindex', '-1');
      heading.focus({ preventScroll: true });
      form.scrollTop = 0;
      dialog.scrollTop = 0;
    }
    function setChoice(name, value) {
      if (!value) return;
      const inputs = $$(`input[name="${name}"]`, form);
      const match = inputs.find(i => i.value.toLowerCase() === value.toLowerCase()) || (name === 'make' && inputs.find(i => i.value === 'Other'));
      if (match) match.checked = true;
    }
    function reset() {
      form.reset();
      syncEmail();
      sent = false;
      showStep(1);
    }

    function open(trigger) {
      source = trigger?.dataset.source || trigger?.closest('[id]')?.id || '';
      if (C.schedulerUrl) {
        track('book_open', { source, method: 'scheduler' });
        window.open(C.schedulerUrl, '_blank', 'noopener');
        return;
      }
      if (sent) reset();
      const service = trigger?.dataset.service;
      setChoice('service', service);
      setChoice('make', trigger?.dataset.make || document.body.dataset.make);
      const topic = trigger?.dataset.note;
      if (topic && !form.elements.message.value.includes(topic)) {
        form.elements.message.value = `Asking about: ${topic}. ${form.elements.message.value}`.trim() + ' ';
      }
      showStep(service ? 2 : step);
      returnFocus = trigger;
      dialog.showModal();
      focusStep();
      track('book_open', { source, service: service || '' });
    }

    document.addEventListener('click', e => {
      const trigger = e.target.closest('[data-book]');
      if (!trigger) return;
      e.preventDefault();
      open(trigger);
    });
    $$('[data-close]', dialog).forEach(b => b.addEventListener('click', () => dialog.close()));
    dialog.addEventListener('click', e => {
      if (e.target !== dialog) return;
      const r = dialog.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close();
    });
    dialog.addEventListener('close', () => returnFocus?.focus());
    backBtn.addEventListener('click', () => { showStep(step - 1); focusStep(); });

    function validate(n) {
      for (const field of $$('input, select, textarea', steps[n - 1])) {
        if (field.classList.contains('hp') || field.checkValidity()) continue;
        field.reportValidity();
        return false;
      }
      return true;
    }

    function collect() {
      const d = Object.fromEntries(new FormData(form));
      const vehicle = [d.year, d.make, d.model].filter(Boolean).join(' ');
      const when = d.date ? new Date(d.date + 'T12:00:00Z').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', timeZone: 'UTC' }) : 'Flexible';
      const summary = [
        'HOUSTON AUTO PROS — APPOINTMENT REQUEST',
        '',
        `Service: ${d.service}`,
        `Vehicle: ${vehicle}${d.mileage ? ` · ${d.mileage} miles` : ''}`,
        `Preferred: ${when}${d.time ? ` · ${d.time}` : ''}`,
        '',
        `Name: ${d.name}`,
        `Phone: ${d.phone}`,
        d.email ? `Email: ${d.email}` : null,
        `Best way to reach me: ${d.contact || 'Call'}`,
        d.message.trim() ? `\nNotes:\n${d.message.trim()}` : null,
      ].filter(line => line !== null).join('\n');
      return { d, vehicle, summary };
    }

    function actionButton(label, href, method, extra = {}) {
      const a = Object.assign(document.createElement('a'), { className: 'button outline-dark', href, ...extra });
      const arrow = Object.assign(document.createElement('span'), { textContent: '↗' });
      arrow.setAttribute('aria-hidden', 'true');
      a.append(label + ' ', arrow);
      a.addEventListener('click', () => track(method === 'call' ? 'call_click' : 'request_fallback', { method, location: 'request' }));
      return a;
    }

    function showResult(kind, data) {
      steps.forEach(s => { s.hidden = true; });
      flow.forEach(el => { el.hidden = true; });
      result.hidden = false;
      const first = (data.d.name || '').trim().split(/\s+/)[0];
      const h = document.createElement('h2');
      const p = document.createElement('p');
      const actions = document.createElement('div');
      actions.className = 'result-actions';
      const fallbacks = () => {
        const body = data.summary;
        if (textNumber) actions.append(actionButton('Text it to the shop', `sms:${textNumber}?&body=${encodeURIComponent(body)}`, 'sms'));
        if (email) actions.append(actionButton('Email it to the shop', `mailto:${email}?subject=${encodeURIComponent('Appointment request — ' + data.vehicle)}&body=${encodeURIComponent(body)}`, 'email'));
        if (phone) actions.append(actionButton(`Call ${phoneLabel}`, 'tel:' + phone, 'call'));
        if (requestUrl) URL.revokeObjectURL(requestUrl);
        requestUrl = URL.createObjectURL(new Blob([body + '\n\nThis request has not been sent. Contact the shop to confirm availability.\n'], { type: 'text/plain' }));
        actions.append(actionButton('Download service brief', requestUrl, 'download', { download: 'houston-auto-pros-service-brief.txt' }));
      };

      if (kind === 'sent') {
        h.textContent = `Thank you${first ? ', ' + first : ''}.`;
        p.textContent = 'Your request has been sent. It isn’t a confirmed booking yet — the shop will contact you to confirm a time.';
        if (phone) actions.append(actionButton(`Prefer to talk? Call ${phoneLabel}`, 'tel:' + phone, 'call'));
      } else if (kind === 'error') {
        h.textContent = 'That didn’t go through.';
        p.textContent = 'Your request was not sent. Try again, or send it another way:';
        const retry = Object.assign(document.createElement('button'), { type: 'button', className: 'button dark', textContent: 'Try again' });
        retry.addEventListener('click', () => { showStep(steps.length); focusStep(); });
        actions.append(retry);
        fallbacks();
      } else {
        h.textContent = 'Your service brief is ready.';
        p.textContent = (phone || textNumber || email)
          ? 'Nothing has been sent. Choose how to share your details with the shop, or download a copy.'
          : 'Download a copy to keep your details together. Nothing has been sent, and no appointment has been booked.';
        fallbacks();
      }

      const details = document.createElement('details');
      details.append(Object.assign(document.createElement('summary'), { textContent: 'View your details' }), Object.assign(document.createElement('pre'), { className: 'request-details', textContent: data.summary }));
      const done = Object.assign(document.createElement('button'), { type: 'button', className: 'text-link', textContent: sent ? 'Close' : '← Edit request' });
      done.addEventListener('click', () => { if (sent) dialog.close(); else { showStep(steps.length); focusStep(); } });
      h.tabIndex = -1;
      result.replaceChildren(h, p, actions, details, done);
      h.focus();
    }

    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (!validate(step)) return;
      if (step < steps.length) {
        track('book_step', { step, source });
        showStep(step + 1);
        focusStep();
        return;
      }
      const data = collect();
      if (form.elements.company.value) { sent = true; showResult('sent', data); return; } // spam trap
      if (!C.requestEndpoint) {
        track('request_prepared', { service: data.d.service, make: data.d.make || '' });
        showResult('draft', data);
        return;
      }
      nextBtn.setAttribute('aria-busy', 'true');
      nextLabel.textContent = 'Sending…';
      try {
        const body = new FormData(form);
        body.delete('company');
        body.append('vehicle', data.vehicle);
        body.append('summary', data.summary);
        body.append('page', location.pathname);
        body.append('_subject', `Appointment request — ${data.vehicle}`);
        Object.entries(attribution).forEach(([k, v]) => body.append(k, v));
        const res = await fetch(C.requestEndpoint, { method: 'POST', body, headers: { Accept: 'application/json' } });
        if (!res.ok) throw new Error(String(res.status));
        sent = true;
        track('generate_lead', { service: data.d.service, make: data.d.make || '', source });
        showResult('sent', data);
      } catch {
        showResult('error', data);
      } finally {
        nextBtn.removeAttribute('aria-busy');
        setNextLabel();
      }
    });

    showStep(1);
  }

  /* ---------- Brand page palette ---------- */
  document.querySelectorAll('[data-color]').forEach(button => button.addEventListener('click', async () => {
    const status = document.querySelector('#color-status');
    try {
      await navigator.clipboard.writeText(button.dataset.color);
      status.textContent = `Copied ${button.dataset.color} to clipboard.`;
    } catch {
      status.textContent = `Color: ${button.dataset.color}`;
    }
  }));
})();
