import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import fs from 'node:fs';
import worker, { validate, messageFor } from '../worker/index.mjs';

const origin = 'https://houston-auto-pros.justin-b75.workers.dev';
function booking(overrides = {}) {
  return { requestId: crypto.randomUUID(), startedAt: String(Date.now() - 5000), service: 'Maintenance & service', make: 'Audi', model: 'A6', year: '2020', mileage: '42000', message: 'QA fixture', name: 'QA request', phone: '7135550100', email: 'justin@aryocg.com', contact: 'Email', date: '', time: 'Morning', page: '/', ...overrides };
}
const form = data => { const body = new FormData(); Object.entries(data).forEach(([key, value]) => body.set(key, value)); return body; };
function environment(t, send = async () => ({ messageId: 'provider-test-receipt' })) {
  const db = new DatabaseSync(':memory:'); db.exec(fs.readFileSync(new URL('../worker/schema.sql', import.meta.url), 'utf8')); t.after(() => db.close());
  return { BOOKING_RECIPIENT: 'justin@aryocg.com', BOOKING_SENDER: 'leads@alerts.homeservicesecretshopper.com',
    APPOINTMENT_EMAIL: { send }, BOOKING_LIMITER: { limit: async () => ({ success: true }) },
    ASSETS: { fetch: async () => new Response('static asset') }, BOOKING_DB: { prepare: sql => ({ bind: (...values) => ({
      run: async () => { const result = db.prepare(sql).run(...values); return { meta: { changes: Number(result.changes) } }; },
      first: async () => db.prepare(sql).get(...values)
    }) }) } };
}
async function submit(env, data, suppliedOrigin = origin) {
  const pending = [], response = await worker.fetch(new Request(origin + '/api/appointments', { method: 'POST', headers: { origin: suppliedOrigin, 'cf-connecting-ip': '192.0.2.10' }, body: form(data) }), env, { waitUntil: promise => pending.push(promise) });
  await Promise.all(pending); return { status: response.status, body: await response.json() };
}

test('broader makes are accepted and malformed contact details are rejected', () => {
  for (const make of ['Audi', 'Bentley', 'Jaguar', 'Land Rover', 'Rolls-Royce', 'Ferrari']) assert.equal(validate(form(booking({ make }))).make, make);
  for (const override of [{ phone: 'bad' }, { email: 'a@b\r\nBcc:bad@example.com' }, { make: 'Invented' }, { name: '' }, { year: '1899' }, { date: '2020-01-01' }, { model: 'A6\r\nInjected subject' }]) assert.throws(() => validate(form(booking(override))));
});
test('email is fixed to the owner, supports visitor replies and escapes HTML', () => {
  const data = booking({ message: '<script>bad</script>', to: 'someone-else@example.com' });
  const message = messageFor(validate(form(data)), 'sender@example.com', 'justin@aryocg.com');
  assert.equal(message.to, 'justin@aryocg.com'); assert.equal(message.replyTo, 'justin@aryocg.com');
  assert.ok(message.html.includes('&lt;script&gt;')); assert.ok(!message.html.includes('<script>'));
});
test('accepted requests send once and retries reuse the receipt', async t => {
  let sends = 0; const env = environment(t, async () => { sends++; return { messageId: 'provider-test-receipt' }; }), data = booking();
  assert.equal((await submit(env, data)).status, 200); assert.equal((await submit(env, data)).status, 200); assert.equal(sends, 1);
  assert.equal((await submit(env, { ...data, model: 'A8' })).status, 409); assert.equal(sends, 1);
});
test('concurrent duplicates cannot send two notifications', async t => {
  let sends = 0; const env = environment(t, async () => { sends++; await new Promise(resolve => setTimeout(resolve, 15)); return { messageId: 'receipt' }; });
  const data = booking(), responses = await Promise.all([submit(env, data), submit(env, data)]);
  assert.equal(sends, 1); assert.ok(responses.some(r => r.status === 200)); assert.ok(responses.some(r => r.status === 503));
  assert.equal((await submit(env, data)).status, 200);
});
test('email failures remain failures and ambiguous sends are not automatically retried', async t => {
  let sends = 0; const env = environment(t, async () => { sends++; throw Error('provider unavailable'); }), data = booking();
  for (let i = 0; i < 2; i++) { const response = await submit(env, data); assert.equal(response.status, 503); assert.equal(response.body.ok, false); }
  assert.equal(sends, 1);
});
test('cross-origin requests, invalid submissions and rate limits cannot send email', async t => {
  let sends = 0; const env = environment(t, async () => { sends++; return { messageId: 'receipt' }; });
  assert.equal((await submit(env, booking(), 'https://other.example')).status, 403);
  assert.equal((await submit(env, booking({ phone: 'bad' }))).status, 400);
  env.BOOKING_LIMITER.limit = async () => ({ success: false });
  assert.equal((await submit(env, booking())).status, 429); assert.equal(sends, 0);
});
test('honeypots suppress notification and static pages retain asset handling', async t => {
  let sends = 0; const env = environment(t, async () => { sends++; return { messageId: 'receipt' }; });
  assert.equal((await submit(env, booking({ company: 'spam' }))).status, 200); assert.equal(sends, 0);
  const response = await worker.fetch(new Request(origin + '/porsche/'), env, {}); assert.equal(await response.text(), 'static asset');
});
