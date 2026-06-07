# 05 — Features / Use Cases (numbered)

Every feature has a stable number `Fxx`. The same numbers appear **in the source code**
as comments (each Lambda has a `Feature: Fxx` docstring; each frontend page has a
`<!-- ... Features: Fxx -->` comment; `api.js` lists the features it covers). This
satisfies the requirement to number each feature and annotate, in the code, which
feature(s) each file implements.

## Actors / permission groups
- **Guest** — unauthenticated invitee (uses a personal RSVP link only).
- **Host** (Cognito group `host`) — authenticated event organizer; manages **their own**
  event. New sign-ups are auto-added to this group by a Post-Confirmation trigger.
- **Admin** (Cognito group `admin`) — platform administrator; manages **all** events.

## Feature catalog

| # | Feature | Actor | Frontend | Backend (route → Lambda) |
| --- | --- | --- | --- | --- |
| F01 | Sign up (email + password) | Host | `signup.html` | Cognito `SignUp` |
| F02 | Confirm email & resend code | Host | `signup.html` | Cognito `ConfirmSignUp` / `ResendConfirmationCode` |
| F03 | Sign in | Host/Admin | `login.html` | Cognito `InitiateAuth` |
| F04 | Reset forgotten password | Host | `forgot.html` | Cognito `ForgotPassword` / `ConfirmForgotPassword` |
| F05 | Sign out / session management | Host/Admin | all authed pages, `api.js` | client-side token clear |
| F06 | Create event | Host | `create-host.html` | `POST /hosts` → `add_host` |
| F07 | View event dashboard | Host | `host.html` | `GET /hosts` → `get_host` |
| F08 | Edit event details & categories | Host | `host.html` | `PUT /hosts` → `update_host` |
| F09 | Delete event | Host | `host.html` | `DELETE /hosts` → `delete_host` |
| F10 | Define tables & capacities | Host | `host.html` | `POST /tables` → `set_tables` |
| F11 | Add guest | Host | `host.html` | `POST /guests` → `add_guest` |
| F12 | List guests | Host | `host.html` | `GET /guests` → `get_guests` |
| F13 | Update guest / assign seat | Host | `host.html`, `guest.html` | `PUT /guests` → `update_guest` |
| F14 | Delete guest | Host | `host.html`, `guest.html` | `DELETE /guests` → `delete_guest` |
| F15 | Guest RSVP via public link | Guest | `rsvp.html` | `POST /guests/rsvp` → `rsvp_guest` |
| F16 | Automatic seating generation | Host | `host.html` | `POST /seating` → `generate_seating` |
| F17 | Send invitations (one / all) | Host | `host.html` | `POST /invitations/send` → `send_invitation` |
| F18 | Admin: list & manage all events | Admin | `admin.html` | `GET /admin/hosts` → `list_hosts` |
| F19 | Shareable no-login preview / demo link | Host (shares) | `host.html?host=`, `guest.html?host=` | reuses `get_host` / `get_guests` |
| F20 | Auto-assign new sign-ups to the `host` group | System (Cognito trigger) | — | `auth_post_confirmation` (Post-Confirmation) |

## Use cases (detail)

### UC-F01/F02 — Register a host account
1. Visitor opens `signup.html`, enters name, email, password.
2. Cognito creates the user and emails a 6-digit code.
3. Visitor enters the code (or requests a resend) to confirm the account.

### UC-F03/F05 — Sign in and out
1. Host enters email + password on `login.html`.
2. On success, tokens are stored in `localStorage` (`seatme_auth`).
3. **Admins** are routed to `admin.html`; hosts to `host.html` (or `create-host.html`
   if they have no event yet).
4. *Log out* clears the stored tokens.

### UC-F04 — Reset a forgotten password
1. Host requests a code on `forgot.html`.
2. Cognito emails a code; host enters it with a new password.

### UC-F06 — Create an event
1. After first sign-in the host fills in event name, date, location.
2. `add_host` creates the item with default categories and empty guests/tables.

### UC-F07/F08/F09 — Manage the event
- View the dashboard (`get_host`), edit details or categories (`update_host`), or
  delete the event and all its guests (`delete_host`).

### UC-F10/F16 — Tables and seating
1. Host defines tables and capacities (`set_tables`).
2. Host clicks **Generate seating**; `generate_seating` seats every `yes` guest,
   keeping categories together, and reports who couldn't be seated.

### UC-F11/F12/F13/F14 — Guest management
- Add (`add_guest`), list (`get_guests`), update or manually seat (`update_guest`),
  delete (`delete_guest`).

### UC-F15 — Guest RSVP (no login)
1. Guest opens their personal link (`rsvp.html?...`).
2. Chooses *yes/no*, sets party size, optional song; `rsvp_guest` saves it.
3. If seated, the page shows their table number.

### UC-F17 — Invitations
- Host emails one guest or the whole list (`send_invitation` via SNS). First contact is
  a one-time *Confirm subscription* email; afterwards links are delivered directly.

### UC-F18 — Admin oversight (second permission group)
1. Admin signs in and lands on `admin.html`.
2. `list_hosts` validates the admin's Cognito **access token** and `admin` group
   membership, then returns **all** events.
3. Admin can **Open** any event (reusing the host dashboard) or **Delete** it.

### UC-F19 — No-login preview / demo link
- A host (or grader) can open `host.html?host=<email>` to view an event **read-only**
  without signing in — the page shows a read-only banner and disables editing, and any
  write is rejected server-side. Signing in as the host or an admin unlocks editing. This
  powers the shareable demo link printed by `redeploy_all.py`.
