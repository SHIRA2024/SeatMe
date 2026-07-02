# 06 — Cost Calculation & Assumptions

Per the requirement, this folder contains (a) the **assumptions** behind the estimate
and (b) a **cost calculation**. The official figures should be produced with the AWS
Pricing Calculator at <https://calculator.aws> using the inputs below, and the shared
link pasted into the placeholder.

> **Action required to finalize:** open <https://calculator.aws>, recreate the line
> items in the *Inputs* table, click **Share**, and paste the generated link here:
>
> **AWS Pricing Calculator link:** `PASTE_CALCULATOR_AWS_SHARE_LINK_HERE`

All prices below are **us-east-1, on-demand, USD**, and are indicative (AWS prices
change). Two columns are shown: with the **AWS Free Tier** and **without** it.

## Workload assumptions (baseline scenario)
| Assumption | Value |
| --- | --- |
| Active hosts (monthly authenticated users) | 50 |
| Events per month | 50 |
| Guests per event | 100 |
| Total guests / RSVPs per month | ~5,000 |
| API requests per month (UI + RSVP + admin) | ~100,000 |
| Lambda invocations per month | ~100,000 |
| Avg Lambda duration / memory | 200 ms @ 128 MB |
| DynamoDB reads / writes per month | ~100,000 / ~100,000 (on-demand) |
| DynamoDB stored data | < 1 GB |
| S3 stored site | ~5 MB |
| S3 GET requests per month | ~500,000 |
| SNS email notifications per month (invites + confirmations) | ~10,000 |

## Per-service estimate (monthly)

| Service | Pricing basis (us-east-1) | Usage | With Free Tier | Without Free Tier |
| --- | --- | --- | --- | --- |
| **Lambda** | $0.20 / 1M requests + $0.0000166667 / GB-s | 100k req, 2,500 GB-s | $0.00 | ~$0.06 |
| **API Gateway (HTTP API)** | $1.00 / 1M requests | 100k req | ~$0.00* | ~$0.10 |
| **DynamoDB (on-demand)** | $1.25 / 1M WRU, $0.25 / 1M RRU + $0.25 / GB | 100k W, 100k R, <1 GB | ~$0.00* | ~$0.20 |
| **S3** | $0.023 / GB + $0.0004 / 1k GET; 100 GB egress free | 5 MB, 500k GET | ~$0.20 | ~$0.20 |
| **Cognito** | First 10,000 MAU free, then $0.0055 / MAU | 50 MAU | $0.00 | ~$0.00 |
| **SNS (email)** | First 1,000 free, then $2.00 / 100k + $0.50 / 1M publishes | 10k emails | ~$0.18 | ~$0.18 |
| **Total** | — | — | **≈ $0.40 / month** | **≈ $0.74 / month** |

\* API Gateway and DynamoDB free-tier allowances (1M HTTP API requests/month and 25 GB
+ provisioned units, respectively) cover this baseline for the 12-month free tier.

## Why it is so low
- **Scales to zero** — no always-on compute; you pay per request/invocation.
- The dominant variable cost is **SNS email** and **API Gateway requests**, both linear
  in the number of guests/RSVPs.

## Sensitivity (scale-up scenario)
If usage grows 20× (1,000 events/month, ~100,000 guests, ~2,000,000 API requests):

| Service | Approx monthly (no free tier) |
| --- | --- |
| Lambda | ~$1.20 |
| API Gateway | ~$2.00 |
| DynamoDB | ~$4.00 |
| S3 | ~$2.00 |
| Cognito (1,000 MAU) | ~$0.00 (under 10k free) |
| SNS email (~200k) | ~$4.00 |
| **Total** | **≈ $13 / month** |

## Notes / caveats
- Figures exclude taxes and any data-transfer beyond the 100 GB/month free egress.
- SES is **not** used (the lab account denies it); invitations use Cognito's built-in
  mailer for verification codes and SNS for invitations, which keeps email cost minimal.
- Re-run the calculator if region, memory size, or average duration change.
