# API Reference

All endpoints are served by a single **API Gateway HTTP API** and backed by one Lambda
function each. The base URL is printed at the end of deployment, e.g.
`https://abc123.execute-api.us-east-1.amazonaws.com`.

- **Content type:** `application/json` for every request with a body.
- **CORS:** open (`*`) for `GET, POST, PUT, DELETE, OPTIONS`.
- **Errors:** failures return a JSON body `{ "message": "..." }` with the status code below.
- **Authentication & authorization:** every **write** endpoint — `POST/PUT/DELETE` on
  `/hosts` and `/guests`, plus `POST /tables`, `POST /seating`, `POST /invitations/send`,
  and `GET /admin/hosts` — requires an `Authorization: Bearer <Cognito access token>`
  header. The Lambda validates the token and confirms the caller either **owns** the
  targeted event (token email == host email) or is an **admin**; otherwise it returns
  `401` (missing/invalid token) or `403` (not the owner/admin). The **read** endpoints
  `GET /hosts`, `GET /guests`, and `POST /guests/rsvp` are **public** by design so the
  RSVP page and the shareable no-login preview keep working.

| Method | Path | Lambda | Purpose |
| --- | --- | --- | --- |
| POST | `/hosts` | `add_host` | Create a host/event |
| GET | `/hosts` | `get_host` | Get a host/event summary |
| PUT | `/hosts` | `update_host` | Update event details / categories |
| DELETE | `/hosts` | `delete_host` | Delete a host and all its guests |
| POST | `/guests` | `add_guest` | Add a guest |
| GET | `/guests` | `get_guests` | List all guests of a host |
| PUT | `/guests` | `update_guest` | Update a guest |
| DELETE | `/guests` | `delete_guest` | Remove a guest |
| POST | `/guests/rsvp` | `rsvp_guest` | Record a guest's RSVP |
| POST | `/tables` | `set_tables` | Define tables and capacities |
| POST | `/seating` | `generate_seating` | Auto-assign confirmed guests to tables |
| POST | `/invitations/send` | `send_invitation` | Email RSVP links (one guest or all) |
| GET | `/admin/hosts` | `list_hosts` | (admin only) List every event on the platform |

---

## Hosts

### POST `/hosts` — create host

Request:

```json
{
  "name": "Jane Cohen",
  "email": "host@example.com",
  "event_name": "Jane & Tom's Wedding",
  "event_date": "2026-09-15",
  "event_location": "Tel Aviv"
}
```

- All fields required. `email` must be valid; `event_date` must be `YYYY-MM-DD`.
- The new host starts with empty `guests`/`tables` and default
  `categories` `["Family", "Friends", "Work", "Other"]`.

Responses: `201` created · `400` validation error · `401`/`403` not signed in / not the owner · `409` host already exists.

### GET `/hosts?host_email=host@example.com` — get host

Response `200`:

```json
{
  "email": "host@example.com",
  "name": "Jane Cohen",
  "event_name": "Jane & Tom's Wedding",
  "event_date": "2026-09-15",
  "event_location": "Tel Aviv",
  "tables": { "1": { "capacity": "10" } },
  "categories": ["Family", "Friends", "Work"],
  "guest_count": 12
}
```

Other responses: `400` missing/invalid `host_email` · `404` host not found.

### PUT `/hosts` — update host

Send `host_email` plus any subset of fields to change:

```json
{ "host_email": "host@example.com", "event_location": "Haifa",
  "categories": ["Family", "Friends", "Work", "College"] }
```

- Updatable: `name`, `event_name`, `event_date`, `event_location`, `categories`.
- `categories` must be a list of non-empty strings (duplicates are removed,
  case-insensitively).

Responses: `200` updated · `400` nothing to update / invalid value · `401`/`403` not signed in / not the owner · `404` host not found.

### DELETE `/hosts` — delete host

```json
{ "email": "host@example.com" }
```

Responses: `200` deleted · `401`/`403` not signed in / not the owner · `404` host not found.

---

## Guests

### POST `/guests` — add guest

```json
{
  "host_email": "host@example.com",
  "name": "Daniel Levi",
  "guest_email": "daniel@example.com",
  "category": "Family",
  "count": 2
}
```

- `host_email`, `name`, `guest_email` required. `category` optional; `count` (party size)
  defaults to `1` and must be between `1` and `20`.
- New guests start with `rsvp: "?"` and `table: null`.

Responses: `201` created · `400` validation error · `401`/`403` not signed in / not the owner · `409` host missing or guest already exists.

### GET `/guests?host_email=host@example.com` — list guests

Response `200`:

```json
{
  "guests": {
    "daniel@example.com": {
      "name": "Daniel Levi", "category": "Family",
      "count": "2", "rsvp": "yes", "table": "1"
    }
  }
}
```

Other responses: `400` missing/invalid `host_email` · `404` host not found.

### PUT `/guests` — update guest

Send `host_email` + `guest_email` plus any subset to change:

```json
{ "host_email": "host@example.com", "guest_email": "daniel@example.com",
  "category": "Work", "table": null }
```

- Updatable: `name`, `category`, `rsvp`, `count`, `table`.
- `count` (party size) must be between `1` and `20`.
- `table: null` clears the assignment; a number assigns the guest to that table.

Responses: `200` updated · `400` nothing to update / invalid `count` · `401`/`403` not signed in / not the owner · `404` host or guest not found.

### DELETE `/guests` — remove guest

```json
{ "host_email": "host@example.com", "guest_email": "daniel@example.com" }
```

Responses: `200` deleted · `401`/`403` not signed in / not the owner · `404` host or guest not found.

### POST `/guests/rsvp` — record RSVP

Used by the public guest RSVP page.

```json
{ "host_email": "host@example.com", "guest_email": "daniel@example.com",
  "rsvp": "yes", "count": 2, "song": "Dancing Queen" }
```

- `rsvp` must be `yes`, `no`, or `?`. `count` and `song` are optional.

Responses: `200` updated · `400` validation error · `404` host or guest not found.

---

## Tables & seating

### POST `/tables` — define tables

```json
{
  "host_email": "host@example.com",
  "tables": { "1": { "capacity": 10 }, "2": { "capacity": 8 } }
}
```

- `tables` is a non-empty map of `tableNumber → { capacity }`; each capacity must be a
  positive integer. This **replaces** the host's table configuration.

Responses: `200` saved · `400` validation error · `401`/`403` not signed in / not the owner · `404` host not found.

### POST `/seating` — generate seating

```json
{ "host_email": "host@example.com" }
```

Seats every guest who RSVP'd `yes`, grouping by category. Response `200`:

```json
{
  "message": "Seating generated",
  "total_guests_seated": 42,
  "assignments": { "daniel@example.com": 1, "noa@example.com": 1 }
}
```

Other responses: `400` no tables defined / not enough seats · `401`/`403` not signed in / not the owner · `404` host not found.

---

## Invitations

### POST `/invitations/send` — email RSVP links

```json
{
  "host_email": "host@example.com",
  "site_url": "https://your-bucket.s3-website-us-east-1.amazonaws.com",
  "guest_email": "daniel@example.com",
  "message": "Optional custom note"
}
```

- Omit `guest_email` to invite **every** guest of the host.
- `site_url` is used to build each guest's personal RSVP link; the frontend passes
  `window.location.origin` automatically.
- Guests must confirm an SNS subscription before any invitation is delivered — see
  [architecture.md](architecture.md#invitations-sns).

**Single guest** responses:

- `200` `{ "status": "sent" }` — delivered.
- `202` `{ "status": "pending" }` — a confirmation email was sent; the guest must
  confirm before invitations arrive.
- `404` guest or host not found.

**All guests** response `200`:

```json
{
  "message": "12 sent, 38 awaiting confirmation",
  "sent": ["..."],
  "pending": ["..."],
  "failed": []
}
```

Error responses: `400` missing `host_email` · `401`/`403` not signed in / not the owner · `404` no guests yet · `500` email service unavailable.

---

## Admin

### GET `/admin/hosts` — list all events (admin only)

Returns a summary of every event on the platform. Requires a Cognito **access token**
in the `Authorization` header; the Lambda validates the token (`GetUser`) and confirms
the caller belongs to the `admin` group (`AdminListGroupsForUser`).

Request header:

```
Authorization: Bearer <cognito-access-token>
```

Response `200`:

```json
{
  "total": 2,
  "hosts": [
    { "email": "host@example.com", "name": "Jane Cohen",
      "event_name": "Jane & Tom's Wedding", "event_date": "2026-09-15",
      "event_location": "Tel Aviv", "guest_count": 42 }
  ]
}
```

Other responses: `401` missing/invalid access token · `403` authenticated but not an
admin · `500` server/Cognito error.
