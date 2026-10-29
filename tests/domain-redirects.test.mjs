import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../worker/domain-redirects.mjs';

test('secondary domains point at relevant pages on the fixed primary domain', () => {
  for (const [host, path] of [
    ['houstonbmwpros.com', '/bmw/'],
    ['www.houstonporschepros.com', '/porsche/'],
    ['houstonporschemechanic.com', '/porsche/'],
    ['houstonporscherepair.com', '/porsche/'],
    ['houstonautodiagpro.com', '/services/#diagnostics'],
    ['houstonenginebuilders.com', '/services/#engine-diagnostics'],
    ['www.houstonautopros.com', '/']
  ]) {
    const response = worker.fetch(new Request('https://' + host + '/'));
    assert.equal(response.status, 301);
    assert.equal(response.headers.get('location'), 'https://houstonautopros.com' + path);
  }
});

test('redirects preserve deep paths and tracking parameters without accepting a new target origin', () => {
  const response = worker.fetch(new Request('https://houstonbmwpros.com/services/?utm_source=google&next=https://other.example'));
  const target = new URL(response.headers.get('location'));
  assert.equal(target.origin, 'https://houstonautopros.com');
  assert.equal(target.pathname, '/services/');
  assert.equal(target.searchParams.get('utm_source'), 'google');
  assert.equal(worker.fetch(new Request('https://unknown.example/')).status, 404);
});
