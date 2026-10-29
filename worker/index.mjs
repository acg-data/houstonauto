import makes from '../content/makes.json' with { type: 'json' };

const SERVICES = ['Maintenance & service', 'Diagnostics & repair', 'Brakes & suspension', 'Cooling & air conditioning', 'Pre-purchase inspection', 'Something else'];
const ORIGINS = new Set(['https://houston-auto-pros.justin-b75.workers.dev', 'https://houstonautopros.com', 'https://www.houstonautopros.com']);
const EMAIL = /^[^\s@\r\n]+@[^\s@\r\n]+\.[^\s@\r\n]+$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
/** @param {string} text */
const escape = text => String(text).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char] || char));
/** @param {number} status @param {Record<string, unknown>} body @param {string|null} [origin] */
const reply = (status, body, origin = null) => Response.json(body, { status, headers: {
  'cache-control': 'no-store', 'x-content-type-options': 'nosniff', 'x-robots-tag': 'noindex, nofollow',
  ...(origin && ORIGINS.has(origin) ? { 'access-control-allow-origin': origin, vary: 'Origin' } : {})
} });

/** @param {Request} request */
async function limitedBody(request) {
  if (!request.body) throw Error('empty_body');
  const reader = request.body.getReader(), chunks = []; let length = 0;
  try {
    for (;;) {
      const { done, value } = await reader.read(); if (done) break;
      length += value.byteLength; if (length > 16384) throw Error('body_too_large');
      chunks.push(value);
    }
  } finally { await reader.cancel(); }
  const buffer = new Uint8Array(length); let offset = 0;
  for (const chunk of chunks) { buffer.set(chunk, offset); offset += chunk.byteLength; }
  return new Response(buffer, { headers: { 'content-type': request.headers.get('content-type') || '' } }).formData();
}

/** @param {FormData} form @param {number} [now] */
export function validate(form, now = Date.now()) {
  /** @param {string} key @param {number} [max] */
  const text = (key, max = 120) => {
    const value = form.get(key);
    if (value != null && typeof value !== 'string') throw Error('invalid_field');
    const result = (value || '').trim();
    if (result.length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(result)) throw Error('invalid_field');
    return result;
  };
  const data = { requestId: text('requestId', 36), service: text('service'), make: text('make'), model: text('model'),
    year: text('year', 4), mileage: text('mileage', 20), message: text('message', 3000), name: text('name'), phone: text('phone', 40),
    email: text('email', 254), contact: text('contact', 10), date: text('date', 10), time: text('time', 30), page: text('page', 300) };
  if (!UUID.test(data.requestId) || !SERVICES.includes(data.service) || !makes.includes(data.make)) throw Error('invalid_selection');
  if (data.model.length < 1 || data.name.length < 2 || /[\r\n]/.test(data.model + data.name)) throw Error('missing_details');
  if (!/^[+\d\s().-]+$/.test(data.phone) || !/^\d{7,15}$/.test(data.phone.replace(/\D/g, ''))) throw Error('invalid_phone');
  if (data.email && !EMAIL.test(data.email)) throw Error('invalid_email');
  if (!['Call', 'Text', 'Email'].includes(data.contact) || (data.contact === 'Email' && !data.email)) throw Error('invalid_contact');
  if (data.year && (!/^\d{4}$/.test(data.year) || +data.year < 1900 || +data.year > new Date(now).getUTCFullYear() + 2)) throw Error('invalid_year');
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Chicago' }).format(new Date(now));
  if (data.date && (!/^\d{4}-\d{2}-\d{2}$/.test(data.date) || !Number.isFinite(Date.parse(data.date)) || new Date(data.date).toISOString().slice(0, 10) !== data.date || data.date < today)) throw Error('invalid_date');
  if (!['', 'Early drop-off', 'Morning', 'Midday', 'Afternoon'].includes(data.time)) throw Error('invalid_time');
  const started = Number(text('startedAt', 16));
  if (!Number.isFinite(started) || started > now - 1000 || started < now - 86400000) throw Error('expired_form');
  return data;
}

/** @param {ReturnType<typeof validate>} data @param {string} sender @param {string} recipient */
export function messageFor(data, sender, recipient) {
  const vehicle = [data.year, data.make, data.model].filter(Boolean).join(' ');
  const rows = [
    ['Service', data.service], ['Vehicle', vehicle], ['Mileage', data.mileage || 'Not provided'],
    ['Preferred day', data.date || 'Flexible'], ['Preferred time', data.time || 'Flexible'],
    ['Name', data.name], ['Phone', data.phone], ['Email', data.email || 'Not provided'], ['Contact preference', data.contact],
    ['Notes', data.message || 'None'], ['Source page', data.page || '/'], ['Request ID', data.requestId]
  ];
  return {
    to: recipient, from: { email: sender, name: 'Houston Auto Pros appointments' },
    ...(data.email ? { replyTo: data.email } : {}),
    subject: `Houston Auto Pros appointment request — ${vehicle}`,
    text: 'New appointment request\n\n' + rows.map(([label, value]) => `${label}: ${value}`).join('\n') + '\n\nContact the visitor to confirm availability. This is a request, not a reserved appointment.',
    html: '<h1>New appointment request</h1><table>' + rows.map(([label, value]) => `<tr><th style="text-align:left;padding:8px;vertical-align:top">${escape(label)}</th><td style="padding:8px;white-space:pre-wrap">${escape(value)}</td></tr>`).join('') + '</table><p>Contact the visitor to confirm availability.</p>'
  };
}

export default {
  /** @param {Request} request @param {Env} env @param {ExecutionContext} ctx */
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith('/api/')) return env.ASSETS.fetch(request);
    const origin = request.headers.get('origin');
    if (url.pathname !== '/api/appointments') return reply(404, { ok: false }, origin);
    if (!origin || !ORIGINS.has(origin)) return reply(403, { ok: false, error: 'origin_not_allowed' });
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: {
      'access-control-allow-origin': origin, 'access-control-allow-methods': 'POST', 'access-control-allow-headers': 'content-type', vary: 'Origin'
    } });
    if (request.method !== 'POST') return reply(405, { ok: false, error: 'method_not_allowed' }, origin);
    if (!/^(multipart\/form-data|application\/x-www-form-urlencoded)\b/i.test(request.headers.get('content-type') || '')) return reply(415, { ok: false, error: 'invalid_content_type' }, origin);
    if (Number(request.headers.get('content-length')) > 16384) return reply(413, { ok: false, error: 'body_too_large' }, origin);
    let form, data;
    try {
      form = await limitedBody(request);
      if (form.get('company')) return reply(200, { ok: true }, origin);
      data = validate(form);
    } catch (error) { return reply(error instanceof Error && error.message === 'body_too_large' ? 413 : 400, { ok: false, error: 'check_details' }, origin); }
    const limit = await env.BOOKING_LIMITER.limit({ key: 'appointments:' + (request.headers.get('cf-connecting-ip') || 'unknown') });
    if (!limit.success) return reply(429, { ok: false, error: 'please_wait' }, origin);
    const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(data))))].map(n => n.toString(16).padStart(2, '0')).join('');
    const now = Date.now();
    try {
      const inserted = await env.BOOKING_DB.prepare('INSERT INTO appointment_receipts (request_id, payload_hash, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(request_id) DO NOTHING').bind(data.requestId, hash, 'pending', now, now).run();
      if (inserted.meta.changes !== 1) {
        const receipt = await env.BOOKING_DB.prepare('SELECT payload_hash, status FROM appointment_receipts WHERE request_id = ?').bind(data.requestId).first();
        if (receipt?.payload_hash !== hash) return reply(409, { ok: false, error: 'request_changed' }, origin);
        if (receipt?.status === 'sent') return reply(200, { ok: true, requestId: data.requestId }, origin);
        return reply(503, { ok: false, error: 'delivery_unconfirmed' }, origin);
      }
    } catch { return reply(503, { ok: false, error: 'temporarily_unavailable' }, origin); }
    try {
      const result = await env.APPOINTMENT_EMAIL.send(messageFor(data, env.BOOKING_SENDER, env.BOOKING_RECIPIENT));
      if (!result?.messageId) throw Error('missing_delivery_receipt');
      try {
        await env.BOOKING_DB.prepare('UPDATE appointment_receipts SET status = ?, message_id = ?, updated_at = ? WHERE request_id = ?').bind('sent', result.messageId, Date.now(), data.requestId).run();
      } catch { console.warn(JSON.stringify({ event: 'booking_receipt_update_failed', requestId: data.requestId })); }
      console.log(JSON.stringify({ event: 'booking_email_accepted', requestId: data.requestId, messageId: result.messageId }));
      ctx.waitUntil(env.BOOKING_DB.prepare('DELETE FROM appointment_receipts WHERE created_at < ?').bind(now - 30 * 86400000).run().catch(() => {}));
      return reply(200, { ok: true, requestId: data.requestId }, origin);
    } catch {
      await env.BOOKING_DB.prepare('UPDATE appointment_receipts SET status = ?, updated_at = ? WHERE request_id = ?').bind('uncertain', Date.now(), data.requestId).run().catch(() => {});
      console.warn(JSON.stringify({ event: 'booking_email_unconfirmed', requestId: data.requestId }));
      return reply(503, { ok: false, error: 'delivery_unconfirmed' }, origin);
    }
  }
};
