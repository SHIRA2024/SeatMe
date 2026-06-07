# 01 — Project Proposal

## Project name
**SeatMe** — a serverless event guest-list and seating manager.

## Problem
Planning the guest list and seating for an event (wedding, conference, party) is
usually handled with spreadsheets and group chats. This is error-prone: RSVPs are
scattered, party sizes are forgotten, table capacities are exceeded, and there is no
single place that shows who is coming and where they sit. Organizers also have no easy
way to collect responses from guests who do not want to install an app or create an
account.

## Proposed solution
SeatMe is a cloud, fully serverless web application with two audiences:

- **Hosts** create an event, manage a categorized guest list, define tables and
  capacities, automatically generate a seating plan, and send each guest a personal
  RSVP link by email.
- **Guests** open a personal link (no account, no login) and reply *yes/no*, set their
  party size, and optionally request a song. Their response appears instantly on the
  host's dashboard.

A **platform administrator** can view and manage every event on the platform.

## Target users / permission groups
1. **User (host)** — an authenticated event organizer who manages their own event.
2. **Admin** — a platform administrator who oversees and can manage all events.
3. **Guest** — an unauthenticated invitee who only uses their personal RSVP link.

## Why serverless / cloud
- **Scales to zero** when idle and scales out automatically for bursts (e.g. when
  invitations go out and many guests RSVP at once).
- **No servers to patch or operate** — every component is an AWS managed service.
- **Pay-per-use** — cost is dominated by actual requests, which suits spiky,
  event-driven traffic.

## Core AWS building blocks
| Concern | Service |
| --- | --- |
| Web hosting | Amazon S3 static website |
| Identity & auth | Amazon Cognito User Pool |
| API | Amazon API Gateway (HTTP API) |
| Business logic | AWS Lambda (Python 3.12) |
| Data | Amazon DynamoDB |
| Notifications | Amazon SNS |

## Scope (MVP delivered)
- Host sign-up / sign-in / password reset (Cognito).
- Create / view / edit / delete an event.
- Manage categories, tables and capacities.
- Add / edit / delete guests; manual seat assignment.
- Public RSVP page reachable from a personal link.
- Automatic, category-aware seating generation.
- Email invitations (single or bulk) via SNS.
- Admin portal listing and managing all events.

## Out of scope (future work)
- Attaching a Cognito JWT authorizer to the HTTP API (write endpoints and the admin
  route are currently authorized inside their Lambdas; public reads remain open for RSVP).
- Drag-and-drop seating UI.
- Multiple events per host.

## Success criteria
- A host can go from sign-up to a generated seating plan and sent invitations without
  leaving the browser.
- A guest can RSVP from a link with no account.
- An admin can see every event and open/delete any of them.
- The entire stack deploys from a single command (`python redeploy_all.py`).
