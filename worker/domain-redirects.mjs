const PRIMARY = 'https://houstonautopros.com';
const ROOTS = new Map([
  ['www.houstonautopros.com', '/'],
  ['houstonautodiagpro.com', '/services/#diagnostics'],
  ['houstonbmwpros.com', '/bmw/'],
  ['houstonenginebuilders.com', '/services/#engine-diagnostics'],
  ['houstonporschemechanic.com', '/porsche/'],
  ['houstonporschepros.com', '/porsche/'],
  ['houstonporscherepair.com', '/porsche/']
]);

export default {
  /** @param {Request} request */
  fetch(request) {
    const source = new URL(request.url);
    const host = source.hostname === 'www.houstonautopros.com' ? source.hostname : source.hostname.replace(/^www\./, '');
    const landing = ROOTS.get(host);
    if (!landing) return new Response('Not found', { status: 404 });
    // A fixed primary origin prevents open redirects; existing deep links and campaign queries survive.
    const target = new URL(source.pathname === '/' ? landing : source.pathname, PRIMARY);
    target.search = source.search;
    return new Response(null, { status: 301, headers: {
      location: target.href,
      'cache-control': 'public, max-age=300',
      'x-content-type-options': 'nosniff'
    } });
  }
};
