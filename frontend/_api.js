/**
 * SeatMe – API Layer
 * ==================
 * Connects all UI buttons to Lambda functions via API Gateway.
 *
 * Set the URL after running setup_aws.py:
 *   const API_BASE = "https://<id>.execute-api.us-east-1.amazonaws.com";
 *
 * Include this file in every screen:
 *   <script src="_api.js"></script>
 */

const API_BASE = window.SEATME_API_BASE || "https://REPLACE_WITH_YOUR_API_URL";

// ─── HOST EMAIL (stored in sessionStorage after login) ────────────────────
function getHostEmail() {
  return sessionStorage.getItem('host_email') || '';
}
function setHostEmail(email) {
  sessionStorage.setItem('host_email', email);
}

// ─── HTTP helpers ──────────────────────────────────────────────────────────
async function apiGet(path, params = {}) {
  const url = new URL(API_BASE + path);
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  const res = await fetch(url);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function apiPut(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function apiDelete(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

// ═══════════════════════════════════════════════════════════════════════════
// HOST
// ═══════════════════════════════════════════════════════════════════════════

/** Event settings screen – saveSettings() */
async function saveSettings() {
  const email      = getHostEmail();
  const name       = document.getElementById('eventName')?.value?.trim();
  const event_name = name;
  const event_date = document.getElementById('eventDate')?.value?.trim();
  const location   = document.getElementById('eventLocation')?.value?.trim();
  const capacity   = parseInt(document.getElementById('eventCapacity')?.value) || 0;

  if (!email) { alert('יש להתחבר תחילה'); window.location.href = 'SCD540~1.HTM'; return; }

  // Try update first; if host doesn't exist, create it
  let data = await apiPut('/hosts', { email, name, event_name, event_date, location, capacity });
  if (data.message === 'Host not found') {
    data = await apiPost('/hosts', { email, name, event_name, event_date, location, capacity });
  }
  if (data.email || data.message === 'Host updated') {
    sessionStorage.removeItem('_seatme_host');
    alert('Settings saved ✓');
  } else {
    alert('Error: ' + (data.message || JSON.stringify(data)));
  }
}

/** Register screen – handleRegister() – calls add_host Lambda (POST /hosts) */
async function registerHost({ name, email, event_name, event_date, event_location }) {
  return apiPost('/hosts', { name, email, event_name, event_date, event_location });
}

/** Login screen – handleLogin() */
async function handleLogin(e) {
  e?.preventDefault();
  const email = document.getElementById('email')?.value?.trim();
  const data  = await apiGet('/hosts', { host_email: email });
  if (data.email) {
    setHostEmail(email);
    location.href = 'SC2B1E~1.HTM';
  } else {
    alert('Host not found: ' + (data.message || ''));
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// GUESTS
// ═══════════════════════════════════════════════════════════════════════════

/** Add guest screen – saveGuest() */
async function saveGuest() {
  const host_email  = getHostEmail();
  const name        = document.getElementById('guestName')?.value?.trim();
  const guest_email = document.getElementById('guestEmail')?.value?.trim();
  const category    = document.querySelector('.tag-chip.selected')?.textContent?.trim() || '';
  const count       = parseInt(document.getElementById('guestCount')?.textContent) || 1;

  if (!host_email || !name || !guest_email) {
    alert('Name, guest email and host email are required');
    return;
  }

  const data = await apiPost('/guests', { host_email, name, guest_email, category, count });
  if (data.guest_email) {
    alert('Guest added ✓');
    location.href = 'SC9376~1.HTM';
  } else {
    alert('Error: ' + (data.message || JSON.stringify(data)));
  }
}

/** Edit guest screen – saveChanges() */
async function saveChanges() {
  const host_email  = getHostEmail();
  const guest_email = sessionStorage.getItem('current_guest_email') || '';
  const name        = document.getElementById('guestName')?.value?.trim();
  const category    = document.querySelector('.tag-chip.selected')?.textContent?.trim() || '';
  const count       = parseInt(document.getElementById('guestCount')?.value) || 1;
  const tableEl     = document.getElementById('tableNumber');
  const tableVal    = tableEl?.value || '';
  const table       = tableVal && tableVal !== '0' && tableVal !== '' ? tableVal : null;
  const rsvp        = document.querySelector('.rsvp-status-box.active-confirmed') ? 'yes'
                    : document.querySelector('.rsvp-status-box.active-declined')  ? 'no' : '?';

  const data = await apiPut('/guests', { host_email, guest_email, name, category, count, table, rsvp });
  if (data.guest_email || data.message === 'Guest updated') {
    alert('השינויים נשמרו ✓');
  } else {
    alert('שגיאה: ' + (data.message || JSON.stringify(data)));
  }
}

/** Edit / guest profile screen – confirmDelete() */
async function confirmDelete() {
  const host_email  = getHostEmail();
  const guest_email = sessionStorage.getItem('current_guest_email') || '';

  const data = await apiDelete('/guests', { host_email, guest_email });
  if (data.message === 'Guest deleted') {
    alert('Guest deleted');
    location.href = 'SC9376~1.HTM';
  } else {
    alert('Error: ' + (data.message || JSON.stringify(data)));
  }
}

/** Load guest list – call on page load */
async function loadGuests() {
  const host_email = getHostEmail();
  if (!host_email) return [];
  const data = await apiGet('/guests', { host_email });
  return data.guests ? Object.entries(data.guests).map(([email, g]) => ({ email, ...g })) : [];
}

// ═══════════════════════════════════════════════════════════════════════════
// RSVP
// ═══════════════════════════════════════════════════════════════════════════

/** Guest RSVP screen – submitRSVP() */
async function submitRSVP() {
  // host_email and guest_email come from URL query params
  const params      = new URLSearchParams(location.search);
  const host_email  = params.get('host') || '';
  const guest_email = params.get('guest') || '';
  const attending   = document.getElementById('btnYes')?.classList.contains('active');
  const rsvp        = attending ? 'yes' : 'no';
  const countEl     = document.getElementById('guestCountDisplay');
  const count       = parseInt(countEl?.value || countEl?.textContent) || 1;
  const song        = document.getElementById('songRequest')?.value?.trim() || '';

  const data = await apiPost('/guests/rsvp', { host_email, guest_email, rsvp, count, song });
  if (data.guest_email || data.rsvp) {
    location.href = `SCREEN~3.HTM?guest=${encodeURIComponent(guest_email)}`;
  } else {
    alert('שגיאה: ' + (data.message || JSON.stringify(data)));
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// TABLES & SEATING
// ═══════════════════════════════════════════════════════════════════════════

/** Table management screen – autoGenerate() */
async function autoGenerate() {
  const host_email = getHostEmail();
  const data = await apiPost('/seating', { host_email });
  if (data.seating || data.message === 'Seating generated') {
    alert('Seating arrangement generated ✓');
    location.reload();
  } else {
    alert('Error: ' + (data.message || JSON.stringify(data)));
  }
}
