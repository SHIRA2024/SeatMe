# SeatMe Installation Guide

## Project Overview

SeatMe is a cloud-based serverless event management system designed to help event hosts manage guests, RSVP responses, and seating arrangements.

The system is built using AWS cloud services and includes:

* Backend AWS Lambda functions
* Amazon DynamoDB database
* Frontend prototype screens

---

## Current Project Status

At the current development stage, the project includes:

* DynamoDB single-table database (host-centric design with nested guests and tables)
* 11 Lambda functions with input validation
* Automated Lambda deployment script
* Greedy seating arrangement algorithm (groups guests by category)
* Seed data and big example test script (50 guests)
* Frontend prototype screens
* Project documentation
* GitHub project repository

### Not Yet Implemented

* Amazon API Gateway (Lambda functions are invoked directly)
* Frontend deployment to Amazon S3
* Amazon SNS messaging service
* User authentication
* System monitoring and logging

---

## Technologies Used

### AWS Services

* Amazon DynamoDB
* AWS Lambda

### Programming Languages

* Python 3.12
* HTML
* CSS

---

## DynamoDB Architecture

The project uses a host-centric single-table design in DynamoDB.

Table name: **SeatMe**

Partition key: `email` (String) — the host's email address.

Each host row contains:

| Field | Type | Description |
|---|---|---|
| email | String | Host email (partition key) |
| name | String | Host name |
| event_name | String | Event name |
| event_date | String | Event date (YYYY-MM-DD) |
| event_location | String | Event location |
| guests | Map | Nested map keyed by guest email |
| tables | Map | Nested map keyed by table number |

Each guest entry inside the `guests` map contains:

| Field | Type | Description |
|---|---|---|
| name | String | Guest name |
| rsvp | String | yes / no / ? |
| table | Number or null | Assigned table number |
| category | String | Guest category (family, friend, work, etc.) |
| count | Number | Number of people in this invite (default 1) |

Each table entry inside the `tables` map contains:

| Field | Type | Description |
|---|---|---|
| capacity | Number | Number of seats at this table |

---

## Lambda Functions

The project includes 11 Lambda functions:

| Function | Description |
|---|---|
| add_host | Create a new host with event details |
| delete_host | Delete a host and all their data |
| get_host | Get host info (event details, tables, guest count) |
| update_host | Update host name or event details |
| add_guest | Add a guest to a host's guest list |
| delete_guest | Remove a guest from the list |
| get_guests | Get all guests for a host |
| update_guest | Update guest name, table, category, or count |
| rsvp_guest | Set a guest's RSVP to yes, no, or ? |
| set_tables | Define tables and their capacities |
| generate_seating | Auto-assign confirmed guests to tables by category |

All functions use:
* Runtime: Python 3.12
* Timeout: 10 seconds
* Memory: 128 MB
* IAM Role: LabRole

---

## Setup Instructions

### Step 1 – Open AWS Academy Learner Lab

1. Open AWS Academy Learner Lab.
2. Click **Start Lab**.
3. Wait until the AWS indicator becomes green.
4. Open AWS Console.

---

### Step 2 – Open CloudShell

1. Open CloudShell inside AWS Console.

---

### Step 3 – Create the DynamoDB Table

Upload `database/create_single_table.py` to CloudShell and run:

```bash
python3 create_single_table.py
```

This creates the **SeatMe** DynamoDB table with PAY_PER_REQUEST billing.

---

### Step 4 – Insert Seed Data (Optional)

Upload `database/seed_single_table.py` to CloudShell and run:

```bash
python3 seed_single_table.py
```

This inserts one example host with 2 guests and 3 tables.

---

### Step 5 – Deploy Lambda Functions

Upload all files from `backend/lambdas/` to CloudShell and run:

```bash
python3 deploy_lambdas.py
```

This automatically creates (or updates) all 11 Lambda functions.

---

### Step 6 – Run the Big Example (Optional)

After deploying the Lambda functions, run the test script:

```bash
python3 big_example.py
```

This creates a host with 50 guests across 4 categories (family, friend, work, neighbor), sets RSVPs, defines 8 tables, generates seating, and prints a seating diagram.

---

## Expected Result

After running the setup:

* **DynamoDB**: AWS Console → DynamoDB → Tables → **SeatMe** — contains host records with nested guest and table data.
* **Lambda**: AWS Console → Lambda → Functions — 11 functions named `SeatMe-{function_name}`.

---

## Important Notes

* Do not click **Reset** in AWS Academy Learner Lab — it permanently deletes all AWS resources.
* The project uses the **us-east-1** AWS region.
* All project code should be backed up regularly to GitHub.
* Lambda functions are currently invoked directly (no API Gateway yet).

---

## Future Deployment Steps

* API Gateway configuration for HTTP endpoints
* Frontend deployment to Amazon S3
* Amazon SNS notifications
* User authentication
* System monitoring and logging
