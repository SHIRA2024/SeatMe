# 09 — Source Code, API Spec & Installation

## Source code
All source code is in this repository (the working app lives at the repo root, not
inside `submission/`):

- **Frontend:** [../../frontend](../../frontend) — vanilla HTML/CSS/JS, one file per
  screen, plus `api.js` (API client) and `app.css`.
- **Backend (microservices):** [../../backend/lambdas](../../backend/lambdas) — 13 AWS
  Lambda handlers (one file per operation) plus a Cognito Post-Confirmation trigger
  (`auth_post_confirmation`) and a shared `_common.py` auth helper. Every handler is
  **self-documented** with a `Feature: Fxx` docstring and inline validation comments.
- **Provisioning / deploy scripts:** [../../backend/deploy](../../backend/deploy) and
  [../../frontend/deploy_frontend.py](../../frontend/deploy_frontend.py).
- **One-command orchestrator:** [../../redeploy_all.py](../../redeploy_all.py).
- **Database scripts:** [../../database](../../database).

## API specification (Swagger / OpenAPI)
The full API is documented as an **OpenAPI 3.0** spec covering all 13 routes (paths,
methods, parameters, request/response schemas, status codes, and the admin security
scheme):

- **Spec file:** [../../backend/api/openapi.yaml](../../backend/api/openapi.yaml)
- **Browsable Swagger UI:** [../../backend/api/index.html](../../backend/api/index.html)
  — open it through a local web server so the browser can load the spec:
  ```bash
  cd backend/api
  python -m http.server 8000
  # then open http://localhost:8000/
  ```
- You can also paste `openapi.yaml` into <https://editor.swagger.io> to view it.

A human-readable companion reference is in [../../docs/api.md](../../docs/api.md).

## Installation instructions
Full instructions are in [../../docs/installation.md](../../docs/installation.md). The
short version (from the **repository root**, region `us-east-1`):

```bash
# 1. install the single dependency (CloudShell already has it)
pip install -r requirements.txt

# 2. deploy the whole serverless stack and load demo data
python3 redeploy_all.py --seed
```

The script prints the **Website URL**, the **API URL**, and a **demo host link**. Other
modes:

| Command | What it does |
| --- | --- |
| `python3 redeploy_all.py` | Deploy without demo data |
| `python3 redeploy_all.py --seed` | Deploy and load demo data |
| `python3 redeploy_all.py --clean --yes --seed` | Wipe, then deploy fresh with demo data |
| `python3 redeploy_all.py --teardown --yes` | Remove all SeatMe AWS resources |

### What gets deployed
1. DynamoDB table `SeatMe`.
2. 13 API Lambda functions + the Cognito Post-Confirmation trigger + API Gateway HTTP API (`setup_aws.py`).
3. Cognito user pool + app client + `host`/`admin` groups + Post-Confirmation trigger
   wiring + seeded admin/host users (`setup_cognito.py`).
4. (with `--seed`) demo data (`seed_example.py`).
5. Frontend uploaded to S3 with the API URL and Cognito IDs injected
   (`deploy_frontend.py`).

## Self-documentation
- Each Lambda begins with a docstring naming its **Feature** and route.
- `frontend/api.js` documents every route→Lambda mapping at the top of the file.
- Validation rules are commented inline in each handler.
