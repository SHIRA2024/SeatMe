# SeatMe Installation Guide

## Project Overview

SeatMe is a cloud-based serverless event management system designed to help event hosts manage guests, RSVP responses, and seating arrangements.

The system is built using AWS cloud services and includes:

* Frontend web application
* Backend AWS Lambda functions
* Amazon DynamoDB database
* Amazon API Gateway
* Amazon SNS messaging service
* Seating arrangement algorithm

---

## Current Project Status

At the current development stage, the project includes:

* DynamoDB single-table database design
* Seed data scripts
* Frontend prototype screens
* Backend Lambda structure
* Initial project documentation
* GitHub project repository

Additional deployment steps will be added as the project progresses.

---

## Technologies Used

### AWS Services

* Amazon DynamoDB
* AWS Lambda
* Amazon API Gateway
* Amazon S3
* Amazon SNS

### Programming Languages

* Python
* HTML
* CSS
* JavaScript

---

## DynamoDB Architecture

The project uses a Single Table Design approach in DynamoDB.

Table name:

* SeatMe

The table stores all system entities using the `entityType` attribute.

Current entity types:

* HOST
* EVENT
* GUEST
* TABLE

This approach simplifies data management and follows DynamoDB best practices for small serverless applications.

---

## DynamoDB Setup Instructions

### Step 1 – Open AWS Academy Learner Lab

1. Open AWS Academy Learner Lab.
2. Click **Start Lab**.
3. Wait until the AWS indicator becomes green.
4. Open AWS Console.

---

### Step 2 – Open CloudShell

1. Open CloudShell inside AWS Console.
2. Upload the following file:

database/create_single_table.py

---

### Step 3 – Create the DynamoDB Table

Run:

```bash
python3 create_single_table.py
```

This script creates the DynamoDB table:

* SeatMe

---

### Step 4 – Insert Seed Data

Upload:

database/seed_single_table.py

Run:

```bash
python3 seed_single_table.py
```

This script inserts example data into the SeatMe table.

Example records include:

* One host
* One event
* Example guests
* Example seating tables

---

## Expected Result

After running the scripts, the following table should appear:

AWS Console → DynamoDB → Tables → SeatMe

The table should contain example records for development and testing purposes.

---

## Important Notes

* Do not click **Reset** in AWS Academy Learner Lab.
* Reset permanently deletes all AWS resources created in the lab.
* The project currently uses the **us-east-1** AWS region.
* All project code should be backed up regularly to GitHub.
* The SeatMe table serves as the primary data store for the application.

---

## Future Deployment Steps

The final version of this guide will later include:

* Lambda deployment instructions
* API Gateway configuration
* Frontend deployment to Amazon S3
* SNS configuration
* Full system deployment process
* Production architecture setup
* User authentication configuration
* System monitoring and logging
