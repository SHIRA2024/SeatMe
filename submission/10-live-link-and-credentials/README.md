# 10 — Live Link, Sample Users & Git Repository

This page provides the live demo link, one login per user type with passwords, and the
Git repository link, as required.

## Live application
> The website URL is account-specific and is printed at the end of `redeploy_all.py`
> (format: `http://seatme-<account-id>.s3-website-us-east-1.amazonaws.com`). Paste your
> deployed URL here:

- **Live site:** `PASTE_LIVE_WEBSITE_URL_HERE`
- **Swagger UI (API):** open `backend/api/index.html` via a local server (see
  [../09-source-and-api](../09-source-and-api/README.md)).
- **No-login demo (host) link:** `PASTE_LIVE_WEBSITE_URL_HERE/host.html?host=demo@seatme.app`

## Git repository
- **Repository:** `PASTE_GIT_REPOSITORY_URL_HERE`

## Sample users (one per permission group)
These users are **seeded automatically** by `backend/deploy/setup_cognito.py`. Change
the passwords before any real use.

| Role / group | Where to sign in | Email | Password |
| --- | --- | --- | --- |
| **Admin** (group `admin`) | `login.html` → routed to `admin.html` | `admin@seatme.app` | `12345678` |
| **User / Host** (group `host`) | `login.html` → routed to `host.html` | `demo@seatme.app` | `12345678` |
| **Guest** (no account) | personal RSVP link only | — (anonymous) | — (no password) |

### Notes
- The **Guest** role is unauthenticated by design — guests only ever use their personal
  RSVP link (`rsvp.html?...`), so there is no guest username/password.
- The seeded passwords can be overridden at deploy time with environment variables:
  `SEATME_ADMIN_PASSWORD`, `SEATME_HOST_PASSWORD` (and `SEATME_ADMIN_EMAIL`,
  `SEATME_HOST_EMAIL`).
- The **Host** demo user (`demo@seatme.app`) owns the seeded example event, so signing
  in as the host shows a populated dashboard. The **Admin** user has no event of its own
  and lands directly on the admin portal listing all events.

## How to verify each role quickly
1. **Admin:** sign in with the admin credentials → you should land on the admin portal
   and see every event; click **Open** on any event to manage it.
2. **Host:** sign in with the host credentials → you should land on the populated event
   dashboard.
3. **Guest:** from the host dashboard, open a guest and copy their personal RSVP link
   (or use the seeded demo link), then open it in a private window — it should let you
   RSVP with no login.
