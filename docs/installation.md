# Installation & Deployment

SeatMe deploys to AWS with a single command. It is designed for the **AWS Academy
Learner Lab** but works in any AWS account whose execution role can manage DynamoDB,
Lambda, API Gateway, Cognito, SNS, and S3.

## Prerequisites

- An AWS account (or an active **AWS Academy Learner Lab**), region **`us-east-1`**.
- **AWS CloudShell** (recommended) — it already has Python 3.12, `boto3`, and the AWS CLI
  with credentials configured.
- If running locally instead: Python 3.12, the AWS CLI configured with credentials, and
  the dependency installed:
  ```bash
  pip install -r requirements.txt
  ```

---

## Option A — one-command deploy (recommended)

From the **repository root**:

```bash
python3 redeploy_all.py --seed
```

This runs the full pipeline and prints the **API URL** and **Website URL** at the end:

1. Create the DynamoDB table `SeatMe`.
2. Deploy the 13 API Lambda functions (plus the Cognito Post-Confirmation trigger) and
   wire up the HTTP API Gateway.
3. (`--seed`) Load demo data — one host and 50 guests.
4. Create the Cognito user pool + app client + `host`/`admin` groups + seeded users.
5. Upload the frontend to S3 and inject the API URL and Cognito IDs.

### Commands

| Command | What it does |
| --- | --- |
| `python3 redeploy_all.py` | Deploy without demo data |
| `python3 redeploy_all.py --seed` | Deploy **and** load demo data |
| `python3 redeploy_all.py --clean --yes` | Delete everything first, then deploy fresh |
| `python3 redeploy_all.py --teardown --yes` | Remove all SeatMe AWS resources |

> `--clean` and `--teardown` are destructive (they delete the table and all data, the
> Cognito user pool, and the S3 site). Without `--yes` you'll be asked to confirm.

When it finishes, open the **Website URL** to use the app.

> With `--seed`, the script also prints a **Demo host** link
> (`.../host.html?host=demo@seatme.app`) that opens the seeded example dashboard
> **without signing in** — handy for sharing a **read-only** demo (editing requires
> signing in as the host or an admin).

---

## Option B — step by step (advanced)

Useful for understanding each stage or deploying pieces individually.

**1. Create the database table**

```bash
aws dynamodb create-table --table-name SeatMe \
  --attribute-definitions AttributeName=email,AttributeType=S \
  --key-schema AttributeName=email,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST --region us-east-1
```

**2. Deploy the backend (Lambdas + API Gateway)**

```bash
cd backend/deploy
python3 setup_aws.py
```

Note the **`API_BASE_URL`** it prints.

**3. Set up authentication (Cognito)**

```bash
python3 setup_cognito.py
```

Note the **`USER_POOL_ID`** and **`CLIENT_ID`** it prints.

**4. Deploy the frontend**

```bash
cd ../../frontend
python3 deploy_frontend.py \
  --api-url       <API_BASE_URL> \
  --user-pool-id  <USER_POOL_ID> \
  --client-id     <CLIENT_ID>
```

It prints the **Website URL**.

**5. (Optional) Load demo data** — only after the Lambdas exist:

```bash
cd ../backend/deploy
python3 seed_example.py
```

---

## Updating an existing deployment

Re-running the deploy is safe and idempotent — existing resources are updated in place:

```bash
python3 redeploy_all.py          # updates Lambda code, re-uploads the frontend
```

To rebuild everything from a clean slate:

```bash
python3 redeploy_all.py --clean --yes --seed
```

## Teardown

```bash
python3 redeploy_all.py --teardown --yes
```

Removes the S3 site, API Gateway, Lambda functions, DynamoDB table, and Cognito user pool.

---

## Email delivery notes

- **Cognito codes** (sign-up / password reset) are sent by Cognito's built-in mailer by
  default and may land in **spam**. `setup_cognito.py` can optionally route them through
  Amazon SES if a verified sender is available; in restricted lab accounts where SES is
  blocked, it automatically falls back to the built-in mailer.
- **Invitations** go out via Amazon SNS. The first message a guest receives is a one-time
  **"Confirm subscription"** email — they must confirm before any invitation is delivered.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `AccessDenied` on SES during deploy | Expected in lab accounts — deployment continues; Cognito uses its built-in mailer. |
| Verification / invitation email missing | Check the **spam** folder; for invitations confirm the SNS subscription first. |
| Frontend loads but API calls fail | Re-run `redeploy_all.py` so the API URL is re-injected into the site. |
| "Sign-in is not configured" | The site was uploaded without Cognito IDs — redeploy so they're injected. |
| Lab reset | Don't click **Reset** in the Learner Lab; it wipes resources. Redeploy if it happens. |

> Keep everything in region **`us-east-1`**.
