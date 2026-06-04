# SeatMe Installation Guide

## Project Overview

SeatMe is a cloud-based serverless event management system designed to help event hosts manage guests, RSVP responses, seating arrangements, and invitation delivery.

The system is built using AWS cloud services and includes:

* AWS Lambda backend
* Amazon DynamoDB database
* Amazon API Gateway
* Amazon SNS email notifications
* Amazon S3 frontend hosting

---

## Current Project Status

At the current development stage, the project includes:

* DynamoDB single-table database (host-centric design with nested guests and tables)
* 12 Lambda functions with input validation
* Automated AWS deployment script
* API Gateway integration
* S3-hosted frontend
* SNS-based invitation delivery
* RSVP management
* Greedy seating arrangement algorithm (groups guests by category)
* Seed data and testing scripts
* Project documentation
* GitHub repository

---

## Technologies Used

### AWS Services

* Amazon DynamoDB
* AWS Lambda
* Amazon API Gateway
* Amazon SNS
* Amazon S3

### Programming Languages

* Python 3.12
* HTML
* CSS
* JavaScript

---

## DynamoDB Architecture

The project uses a host-centric single-table design.

Table name: **SeatMe**

Partition key:

* `email` (String) — Host email

Each host record contains:

| Field          | Description      |
| -------------- | ---------------- |
| email          | Host email       |
| name           | Host name        |
| event_name     | Event name       |
| event_date     | Event date       |
| event_location | Event location   |
| guests         | Nested guest map |
| tables         | Nested table map |

Each guest contains:

| Field    | Description        |
| -------- | ------------------ |
| name     | Guest name         |
| rsvp     | yes / no / ?       |
| table    | Assigned table     |
| category | Guest category     |
| count    | Number of invitees |

---

## Lambda Functions

The project includes 12 Lambda functions:

| Function         | Description                                         |
| ---------------- | --------------------------------------------------- |
| add_host         | Create host                                         |
| get_host         | Retrieve host                                       |
| update_host      | Update host                                         |
| delete_host      | Delete host                                         |
| add_guest        | Add guest                                           |
| get_guests       | Retrieve guests                                     |
| update_guest     | Update guest                                        |
| delete_guest     | Delete guest                                        |
| rsvp_guest       | Update RSVP                                         |
| set_tables       | Configure tables                                    |
| generate_seating | Generate seating arrangement                        |
| send_invitation  | Send invitation emails and manage SNS subscriptions |

---

## Invitation Flow

The system currently supports invitation delivery through **Email only**.

Flow:

1. Host adds a guest with a real email address.
2. Host clicks **Send Invitation**.
3. If this is the guest's first invitation, AWS SNS sends a subscription confirmation email.
4. Guest confirms the subscription.
5. Host clicks **Send Invitation** again.
6. The actual invitation email is delivered.

Notes:

* Confirmation emails may arrive in Spam.
* WhatsApp and SMS are not currently supported.
* SNS is used for demonstration purposes in AWS Academy.

---

## Setup Instructions

### Step 1 – Start AWS Academy Learner Lab

1. Open AWS Academy Learner Lab.
2. Click **Start Lab**.
3. Wait until AWS becomes available.
4. Open AWS Console.

---

### Step 2 – Open CloudShell

Open CloudShell from the AWS Console.

---

### Step 3 – Create DynamoDB Table

Run:

```bash
python3 create_single_table.py
```

This creates the SeatMe DynamoDB table.

---

### Step 4 – Seed Example Data (Optional)

Run:

```bash
python3 seed_single_table.py
```

This inserts sample hosts, guests, and tables.

---

### Step 5 – Deploy Backend

Navigate to:

```bash
cd ~/SeatMe/backend/lambdas
```

Run:

```bash
python3 setup_aws.py
```

This script automatically:

* Creates or updates Lambda functions
* Creates or updates API Gateway routes
* Configures permissions
* Deploys backend resources

At the end, the script prints an API URL.

---

### Step 6 – Deploy Frontend

Navigate to:

```bash
cd ~/SeatMe/frontend
```

Run:

```bash
python3 deploy_frontend.py --api-url YOUR_API_URL
```

Replace `YOUR_API_URL` with the URL printed by `setup_aws.py`.

At the end, the script prints a Website URL.

Open the Website URL to access the system.

---

## Expected Result

After deployment:

### DynamoDB

* SeatMe table exists
* Hosts, guests, and tables are stored

### Lambda

* 12 SeatMe Lambda functions are deployed

### API Gateway

* REST endpoints are available

### SNS

* Invitation emails can be delivered

### S3

* Frontend is hosted and accessible

---

## Important Notes

* Do NOT click Reset in AWS Academy Learner Lab.
* Use region us-east-1.
* Back up changes regularly to GitHub.
* SNS confirmation emails may arrive in Spam.
* The first invitation triggers SNS subscription confirmation.

---

## Future Improvements

* Replace SNS with Amazon SES for direct email delivery
* User authentication
* Monitoring and logging
* Improved invitation templates
* Production deployment
* Mobile-responsive UI
