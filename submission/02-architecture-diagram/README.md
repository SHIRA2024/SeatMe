# 02 — Architecture Diagram

The architecture diagram uses **official AWS service icons** (the draw.io / AWS 2024
icon set) and is provided together with its **editable source file**, as required.

## Files
- **Source (editable):** [seatme-architecture.drawio](seatme-architecture.drawio)
- **How to open / export:**
  1. Go to <https://app.diagrams.net> (draw.io) and choose *Open Existing Diagram*, or
     open the file with the *Draw.io Integration* VS Code extension.
  2. The icons are AWS4 shapes (`shape=mxgraph.aws4.*`) — they render as the official
     AWS icons automatically.
  3. Export an A4 image with **File → Export as → PNG/PDF**, set *Paper size = A4*, and
     enable *Fit page* so the whole diagram fits one A4 page.

## What the diagram shows
- **Host (browser)** and **Guest (browser)** as external actors.
- An **AWS Cloud (us-east-1)** boundary containing the managed services:
  - **Amazon S3** — static website hosting the HTML/CSS/JS frontend.
  - **Amazon Cognito User Pool** — host identity (sign-up, verification, sign-in,
    reset) and group membership (`host` + `admin`).
  - **Amazon API Gateway (HTTP API)** — single JSON API surface.
  - **AWS Lambda (13 API functions, Python 3.12)** — one per operation — plus a Cognito
    Post-Confirmation trigger Lambda (`auth_post_confirmation`).
  - **Amazon DynamoDB** — single table `SeatMe`.
  - **Amazon SNS** — invitations topic that emails guests their RSVP link.
- **Guest inbox** as the email recipient.

## Key flows (arrows)
1. Host browser **loads the site** from S3.
2. Host browser **authenticates directly** against Cognito (`cognito-idp`).
3. Host browser calls **API Gateway** with JSON (write and admin calls add a Bearer access token).
4. Guest browser calls API Gateway for the **public RSVP** (no login).
5. API Gateway **invokes** Lambda.
6. Lambda reads/writes **DynamoDB** (`GetItem` / `UpdateItem` / `Scan`).
7. Lambda **subscribes/publishes** to SNS for invitations.
8. SNS **emails** the guest their personal RSVP link.
9. Protected Lambdas (writes + admin) **validate the caller's token** against Cognito
   (dashed line: `GetUser` + `AdminListGroupsForUser`).

A full written explanation of each component and flow is in
[../03-architecture-explanation](../03-architecture-explanation/README.md).
