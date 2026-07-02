# 07 — User Guide

This guide covers the two non-administrator user types: the **Host** (event organizer)
and the **Guest** (invitee). The administrator has a separate guide in
[../08-admin-guide](../08-admin-guide/README.md).

The live site URL and sample logins are in
[../10-live-link-and-credentials](../10-live-link-and-credentials/README.md).

---

## Part A — Host guide

### 1. Create an account (Features F01, F02)
1. Open the site and click **Create an account**.
2. Enter your name, email, and a password (minimum 8 characters).
3. Check your inbox for a 6-digit code and enter it to confirm. (Didn't get it? Click
   **Resend code**.)

### 2. Sign in (F03)
- Use your email and password on the **Log in** page. Forgot your password? Use
  **Forgot password?** to email yourself a reset code (F04).

### 3. Create your event (F06)
- The first time you sign in you'll be asked for the **event name, date, and location**.
  Click **Create event**.

### 4. The dashboard (F07)
The dashboard shows your event details, categories, tables, and guest list.

### 5. Edit or delete the event (F08, F09)
- **Edit** changes the name, date, location, or **categories** (the groups used for
  seating, e.g. Family / Friends / Work).
- **Delete event** removes the event and all of its guests (this cannot be undone).

### 6. Define tables (F10)
- Add tables and set each table's **capacity** (number of seats). Saving replaces the
  current table layout.

### 7. Add and manage guests (F11–F14)
- **Add guest:** name, email, category, and **party size** (how many people that one
  invitation covers).
- Click a guest to **open** their details, change their RSVP, party size, category, or
  **assign a table manually**, or **delete** them.

### 8. Generate seating (F16)
- Click **Generate seating**. SeatMe seats every guest who RSVP'd **yes**, keeping each
  category together where possible, and tells you if there aren't enough seats or who
  couldn't be placed.

### 9. Send invitations (F17)
- Send to **one** guest or to **everyone**. Each guest gets a personal RSVP link by
  email.
- **Important:** the first email a guest receives is a one-time *"Confirm subscription"*
  message (from Amazon SNS). They must click **Confirm** once; afterwards invitations
  arrive directly.

### 10. Share a no-login preview (F19)
- You can share `host.html?host=<your-email>` to let someone view the event **read-only**
  without signing in. (This is the same link the deployment prints as the demo link.)
  Editing requires signing in as the host or an admin.

---

## Part B — Guest guide

### 1. Open your invitation (F15)
- Click the **personal link** in the invitation email. No account or password is needed.

### 2. RSVP
1. You'll see the event name, date, and location.
2. Choose **"I'll be there"** or **"Can't make it"**.
3. Set **how many people** are coming (your party size).
4. Optionally add a **song request**.
5. Click **Send response** — it saves instantly.

### 3. Check your seat
- If the host has generated seating, the RSVP page shows **your table number**. You can
  return to the same link anytime to update your response.

---

## Troubleshooting
| Problem | Fix |
| --- | --- |
| No confirmation code email | Check spam; click **Resend code** on the sign-up page. |
| Guest didn't get the invitation | Ask them to look for the SNS *Confirm subscription* email and confirm it once. |
| "Not enough seats" when generating | Add tables/capacity or reduce party sizes, then try again. |
| Numbers look like text | Expected — the API returns numbers as strings; the UI converts them automatically. |
