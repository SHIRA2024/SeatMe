# Features

SeatMe covers the full lifecycle of planning an event's guest list and seating, split
between a **host** experience (manage everything) and a **guest** experience (a simple
RSVP page).

## Screens at a glance

| Screen | File | Audience | Purpose |
| --- | --- | --- | --- |
| Landing | `index.html` | Public | Intro + link to sign in |
| Sign up | `signup.html` | Host | Create account + confirm email code |
| Log in | `login.html` | Host | Sign in |
| Reset password | `forgot.html` | Host | Email a code and set a new password |
| Create event | `create-host.html` | Host | One-time event setup |
| Manage event | `host.html` | Host | The main dashboard |
| Guest details | `guest.html` | Host | View/edit a single guest |
| RSVP | `rsvp.html` | Guest | Public RSVP page (opened from an invitation link) |
| Admin portal | `admin.html` | Admin | View & manage **all** events on the platform |

---

## Host journey

1. **Sign up** with email + password, then enter the 6-digit code emailed by Cognito.
   (Already confirmed? Just **log in**. Forgot your password? Use **reset**.)
2. **Create your event** — name, date, and location. The email comes from your account.
3. On the **dashboard** you can:
   - **Edit event details** or delete the event.
   - **Define tables** and seats per table.
   - **Manage categories** (e.g. Family, Friends, Work) used to group guests.
   - **Add guests** with a name, email, category, and party size.
   - **Generate seating** to auto-fill tables with confirmed guests.
   - **Send invitations** to one guest or the whole list.
4. Open any guest to **edit details**, change their RSVP, or assign a table manually.

## Guest journey

1. The guest receives an **invitation email** with a personal link.
2. The link opens the **RSVP page** showing the event details.
3. They choose **"I'll be there"** or **"Can't make it"**, set how many people are
   coming, and optionally add a **song request**.
4. Their response is saved instantly and reflected on the host's dashboard. If they've
   been seated, the page also shows **their table number**.

---

## Feature details

### Authentication & permissions
Email/password accounts via Amazon Cognito, with email verification, resend-code, and
password reset. Sessions are kept in the browser. Two Cognito groups provide the
permission tiers: **host** (manages their own event) and **admin** (manages every event).
Beyond gating the UI, every write is authorized **server-side** — the caller must own the
targeted event or be an admin — so the shareable no-login preview link is **read-only**.

### Event management
One event per host. Details (name, date, location) are editable at any time; deleting an
event removes all of its guests.

### Guests & categories
Guests are grouped into host-defined **categories**. A guest's **party size** (`count`)
lets one invitation represent several people, which the seating algorithm respects.

### RSVP
Guests reply through a personal link — no account needed. Responses are `yes`, `no`, or
pending, and can include a party size and song request.

### Tables & automatic seating
Define tables and capacities, then generate a plan that seats every confirmed guest and
keeps each category together where possible. The dashboard renders a live seating chart
and lists confirmed guests who couldn't be seated. Seating can also be adjusted by hand
from a guest's details page. See the algorithm in
[architecture.md](architecture.md#seating-algorithm).

### Invitations
Email guests their RSVP link individually or in bulk through Amazon SNS. Because SNS
delivers via topic subscriptions, the first email a guest receives is a one-time
**"Confirm subscription"** message; once confirmed, future invitations are delivered
directly. The bulk action reports how many were sent versus still awaiting confirmation.
