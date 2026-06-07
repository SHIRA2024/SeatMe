# SeatMe — Submission Package

This folder maps the SeatMe project to the required final-project deliverables.
The working application (source code, deploy scripts) lives at the **repository
root** (`backend/`, `frontend/`, `database/`); these numbered folders are the
documentation and submission artifacts, with links back into the code.

| # | Deliverable | Folder |
| --- | --- | --- |
| 01 | Project proposal | [01-proposal](01-proposal/README.md) |
| 02 | Architecture diagram (official AWS icons) + source file | [02-architecture-diagram](02-architecture-diagram/README.md) |
| 03 | Architecture explanation | [03-architecture-explanation](03-architecture-explanation/README.md) |
| 04 | UI design / wireframes | [04-ui-wireframes](04-ui-wireframes/README.md) |
| 05 | Numbered features / use cases (+ code mapping) | [05-features](05-features/README.md) |
| 06 | Cost calculation + assumptions | [06-cost](06-cost/README.md) |
| 07 | User guide (per user type) | [07-user-guide](07-user-guide/README.md) |
| 08 | Administrator guide | [08-admin-guide](08-admin-guide/README.md) |
| 09 | Source code + API spec (Swagger) + install scripts | [09-source-and-api](09-source-and-api/README.md) |
| 10 | Live link + sample users & passwords + Git link | [10-live-link-and-credentials](10-live-link-and-credentials/README.md) |
| 11 | Developer / maintenance docs (microservice interfaces) | [11-developer-docs](11-developer-docs/README.md) |
| 12 | Risk register (Excel) + top-risk mitigation | [12-risk-register](12-risk-register/README.md) |

## Mandatory requirements coverage

| Requirement | Where it is met |
| --- | --- |
| Frontend | `frontend/` — vanilla HTML/CSS/JS on Amazon S3 static hosting |
| Backend | `backend/lambdas/` — 13 API Lambda functions + 1 Cognito trigger (Python 3.12) |
| Authentication requiring identification | Amazon Cognito User Pool (email + password, email verification) |
| At least two permission groups | **host** and **admin** Cognito groups — see 05 & 08 |
| Database | Amazon DynamoDB single table `SeatMe` |
| Serverless | S3 + Cognito + API Gateway + Lambda + DynamoDB + SNS (no servers) |
