/**
 * SeatMe – API Client
 * ===================
 * Maps every UI action to an API Gateway route backed by a Lambda function.
 *
 * The base URL is injected at deploy time by deploy_frontend.py, which replaces
 * the placeholder below. Each page sets `window.SEATME_API_BASE` before loading
 * this file.
 *
 *   Hosts    POST/GET/PUT/DELETE  /hosts
 *   Guests   POST/GET/PUT/DELETE  /guests
 *   RSVP     POST                 /guests/rsvp
 *   Tables   POST                 /tables
 *   Seating  POST                 /seating
 *   Invite   POST                 /invitations/send
 *   Admin    GET                  /admin/hosts
 *
 * Features implemented here: F01-F05 (auth & session), F06-F17 (event/guest
 * actions), F18 (admin oversight), F19 (no-login preview link).
 */

const API_BASE = (window.SEATME_API_BASE || 'https://REPLACE_WITH_YOUR_API_URL').replace(/\/+$/, '');
const API_CONFIGURED = !API_BASE.includes('REPLACE_WITH_YOUR_API_URL');

/* ── AWS Cognito config (injected at deploy time) ───────────────────── */
const COGNITO = {
  region: 'us-east-1',
  userPoolId: 'REPLACE_WITH_COGNITO_USER_POOL_ID',
  clientId: 'REPLACE_WITH_COGNITO_CLIENT_ID',
};
const COGNITO_CONFIGURED = !COGNITO.clientId.startsWith('REPLACE_WITH');

/* ── Session (Cognito tokens) ─────────────────────────────────── */
const AUTH_KEY = 'seatme_auth';
const Session = {
  save: (tokens) => localStorage.setItem(AUTH_KEY, JSON.stringify(tokens)),
  read: () => { try { return JSON.parse(localStorage.getItem(AUTH_KEY) || 'null'); } catch (_) { return null; } },
  getHostEmail: () => { const s = Session.read(); return s ? s.email : ''; },
  getIdToken: () => { const s = Session.read(); return s ? s.idToken : ''; },
  getAccessToken: () => { const s = Session.read(); return s ? s.accessToken : ''; },
  // Cognito groups encoded in the ID token. Used for UI gating only; the
  // backend independently verifies the token + group on admin endpoints.
  groups: () => {
    const t = Session.getIdToken();
    if (!t) return [];
    try {
      const part = t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      return JSON.parse(atob(part))['cognito:groups'] || [];
    } catch (_) { return []; }
  },
  isAdmin: () => Session.groups().includes('admin'),
  isAuthed: () => {
    const s = Session.read();
    return !!(s && s.idToken && (!s.expiresAt || s.expiresAt > Date.now()));
  },
  clear: () => {
    localStorage.removeItem(AUTH_KEY);
    sessionStorage.removeItem('host_cache');
  },
};

/* ── Auth (AWS Cognito User Pools, USER_PASSWORD_AUTH) ───────────────── */
async function cognitoCall(action, payload) {
  if (!COGNITO_CONFIGURED) {
    const e = new Error('Sign-in is not configured yet. Redeploy with Cognito enabled.');
    e.code = 'NotConfigured';
    throw e;
  }
  const res = await fetch(`https://cognito-idp.${COGNITO.region}.amazonaws.com/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-amz-json-1.1',
      'X-Amz-Target': `AWSCognitoIdentityProviderService.${action}`,
    },
    body: JSON.stringify(payload),
  });
  let data = {};
  try { data = await res.json(); } catch (_) { /* no body */ }
  if (!res.ok) {
    const code = (data.__type || '').split('#').pop() || 'AuthError';
    const e = new Error(data.message || code);
    e.code = code;
    throw e;
  }
  return data;
}

const Auth = {
  configured: () => COGNITO_CONFIGURED,

  signUp: (email, password) => cognitoCall('SignUp', {
    ClientId: COGNITO.clientId,
    Username: email,
    Password: password,
    UserAttributes: [{ Name: 'email', Value: email }],
  }),

  confirm: (email, code) => cognitoCall('ConfirmSignUp', {
    ClientId: COGNITO.clientId, Username: email, ConfirmationCode: code,
  }),

  resend: (email) => cognitoCall('ResendConfirmationCode', {
    ClientId: COGNITO.clientId, Username: email,
  }),

  signIn: async (email, password) => {
    const data = await cognitoCall('InitiateAuth', {
      ClientId: COGNITO.clientId,
      AuthFlow: 'USER_PASSWORD_AUTH',
      AuthParameters: { USERNAME: email, PASSWORD: password },
    });
    const r = data.AuthenticationResult;
    if (!r || !r.IdToken) {
      const e = new Error('Could not complete sign-in.');
      e.code = 'NoTokens';
      throw e;
    }
    Session.save({
      email,
      idToken: r.IdToken,
      accessToken: r.AccessToken,
      refreshToken: r.RefreshToken,
      expiresAt: Date.now() + ((r.ExpiresIn || 3600) * 1000),
    });
    return r;
  },

  forgotPassword: (email) => cognitoCall('ForgotPassword', {
    ClientId: COGNITO.clientId, Username: email,
  }),

  confirmForgotPassword: (email, code, password) => cognitoCall('ConfirmForgotPassword', {
    ClientId: COGNITO.clientId, Username: email, ConfirmationCode: code, Password: password,
  }),

  signOut: () => Session.clear(),
};

/* ── Core request helper ──────────────────────────────────────────────── */
async function apiRequest(method, path, { params, body, auth } = {}) {
  if (!API_CONFIGURED) {
    return {
      ok: false,
      status: 0,
      data: { message: 'API URL is not configured. Deploy with: python3 deploy_frontend.py --api-url <url>' },
    };
  }

  const url = new URL(API_BASE + path);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value != null) url.searchParams.set(key, value);
    }
  }

  const options = { method, headers: {} };
  if (auth) {
    const token = Session.getAccessToken();
    if (token) options.headers['Authorization'] = 'Bearer ' + token;
  }
  if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }

  try {
    const res = await fetch(url, options);
    let data = {};
    try { data = await res.json(); } catch (_) { /* empty body */ }
    return { ok: res.ok, status: res.status, data };
  } catch (err) {
    return { ok: false, status: 0, data: { message: 'Network error: ' + err.message } };
  }
}

/* ── Hosts ────────────────────────────────────────────────────────────── */
const Hosts = {
  get:           (host_email)             => apiRequest('GET',    '/hosts', { params: { host_email } }),
  create:        (host)                   => apiRequest('POST',   '/hosts', { body: host, auth: true }),
  update:        (host)                   => apiRequest('PUT',    '/hosts', { body: host, auth: true }),
  remove:        (email)                  => apiRequest('DELETE', '/hosts', { body: { email }, auth: true }),
  setCategories: (host_email, categories) => apiRequest('PUT',    '/hosts', { body: { host_email, categories }, auth: true }),
};

/* ── Guests ───────────────────────────────────────────────────────────── */
const Guests = {
  list:   (host_email)               => apiRequest('GET',    '/guests', { params: { host_email } }),
  add:    (guest)                    => apiRequest('POST',   '/guests', { body: guest, auth: true }),
  update: (guest)                    => apiRequest('PUT',    '/guests', { body: guest, auth: true }),
  remove: (host_email, guest_email)  => apiRequest('DELETE', '/guests', { body: { host_email, guest_email }, auth: true }),
  rsvp:   (payload)                  => apiRequest('POST',   '/guests/rsvp', { body: payload }),
};

/* ── Tables & Seating ─────────────────────────────────────────────────── */
const Tables  = { set:      (host_email, tables) => apiRequest('POST', '/tables',  { body: { host_email, tables }, auth: true }) };
const Seating = { generate: (host_email)         => apiRequest('POST', '/seating', { body: { host_email }, auth: true }) };

/* ── Invitations ──────────────────────────────────────────────────────── */
const Invitations = {
  send: (host_email, guest_email, message) =>
    apiRequest('POST', '/invitations/send', {
      body: { host_email, guest_email, message, site_url: window.location.origin },
      auth: true,
    }),
  sendAll: (host_email, message) =>
    apiRequest('POST', '/invitations/send', {
      body: { host_email, message, site_url: window.location.origin },
      auth: true,
    }),
};

/* ── Admin (members of the Cognito 'admin' group only) ─────────────────── */
const Admin = {
  listHosts: () => apiRequest('GET', '/admin/hosts', { auth: true }),
};

/* ── Shared UI helpers ────────────────────────────────────────────────── */
function emailValid(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function requireHost(redirect = 'login.html') {
  // Preview mode: a `?host=<email>` link opens a host dashboard without signing
  // in. Used for the seeded example host so it can be shared as a public demo.
  const preview = (new URLSearchParams(window.location.search).get('host') || '').trim().toLowerCase();
  if (preview) return preview;
  if (!Session.isAuthed()) { window.location.href = redirect; return null; }
  return Session.getHostEmail();
}

function escapeHtml(value) {
  return (value == null ? '' : String(value)).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

function toast(message, type = 'ok') {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.className = 'toast show ' + (type === 'err' ? 'toast-err' : 'toast-ok');
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.remove('show'), 2800);
}
