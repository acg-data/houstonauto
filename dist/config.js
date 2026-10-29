/*
  Houston Auto Pros — site settings. This is the only file you need to edit for business details.

  Use verified details only. Leave anything you don't have yet empty ('' or null):
  - while showPlaceholders is true, missing details and empty photo slots are outlined
    with a note saying what goes there;
  - when it is false (launch), anything missing is hidden instead.
*/
window.HAP_CONFIG = {
  showPlaceholders: false,
  launchState: 'staging', // switch to production only after business details and booking are verified
  showReviewsPreview: false, // reveal reviews only when real feedback or a profile link is configured

  siteUrl: 'https://houstonautopros.com', // primary domain; keep canonical and social metadata aligned

  phone: '',        // E.164 format, e.g. '+17135550123'
  phoneDisplay: '', // how it should read, e.g. '(713) 555-0123'
  textNumber: '',   // only if this number can receive texts (usually the same as phone)
  email: '',

  address: {
    street: '',
    city: 'Houston',
    region: 'TX',
    postalCode: '',
  },
  mapsUrl: '', // Google Business Profile / Maps link; built from the address when empty
  geo: null,   // optional: { lat: 29.7604, lng: -95.3698 }

  // Opening hours in Houston time. Days: Mo Tu We Th Fr Sa Su. 24-hour times.
  hours: [
    // { days: ['Mo', 'Tu', 'We', 'Th', 'Fr'], opens: '07:30', closes: '17:30' },
  ],

  // Same-origin Worker endpoint; success requires JSON { ok: true } after email acceptance.
  requestEndpoint: 'https://houston-auto-pros.justin-b75.workers.dev/api/appointments',
  bookingEmail: 'justin@aryocg.com',
  // Optional: send "Request a visit" buttons to your shop software's online scheduler instead.
  schedulerUrl: '',

  // Copy these exactly from your Google Business Profile. Never write or edit reviews.
  rating: { value: null, count: null }, // e.g. { value: 4.9, count: 112 }
  reviewsUrl: '',
  reviews: [
    // { quote: '...', name: 'First name L.', car: '2016 Porsche 911', source: 'Google' },
  ],

  sameAs: [], // social profile URLs, e.g. ['https://www.instagram.com/...']

  // Optional analytics. Calls, texts and requests are tracked as conversions.
  ga4Id: '',              // 'G-XXXXXXXXXX'
  googleAdsConversion: '', // 'AW-123456789/AbCdEfGhIj' — fires when a request is sent
  metaPixelId: '',
};
