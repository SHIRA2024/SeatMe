SeatMe Installation Guide
Project Overview

SeatMe is a cloud-based serverless system for managing event invitations, RSVP confirmations, and smart seating arrangements.

The system is built using AWS cloud services and includes:

Frontend web application
Backend Lambda functions
DynamoDB database
API Gateway
SNS messaging integration
Seating arrangement algorithm
Current Project Status

At the current development stage, the project includes:

Initial DynamoDB setup
Seed data scripts
Frontend prototype screens
Backend Lambda structure
Documentation structure

Additional deployment steps will be added later during the project development process.

Technologies Used
AWS Services
Amazon DynamoDB
AWS Lambda
Amazon API Gateway
Amazon S3
Amazon SNS
Programming Languages
Python
HTML
CSS
JavaScript
DynamoDB Setup Instructions
Step 1 — Open AWS Academy Learner Lab
Open AWS Academy Learner Lab.
Click Start Lab.
Wait until the AWS indicator becomes green.
Open AWS Console.
Step 2 — Open CloudShell
Inside AWS Console, open CloudShell.
Upload the following file:

database/create_tables.py

Step 3 — Create DynamoDB Tables

Run the following command:

python3 create_tables.py

This script creates the following tables:

Hosts
Events
Guests
Tables
Step 4 — Insert Seed Data

Upload the following file:

database/seed_data.py

Run:

python3 seed_data.py

This script inserts example data for:

One host
One event
Example guests
Example seating tables
Expected Result

After running the scripts, the DynamoDB tables should appear in:

AWS Console → DynamoDB → Tables

The tables should contain example data for testing and development.

Important Notes
Do not click Reset in AWS Academy Learner Lab.
Reset permanently deletes all AWS resources created in the lab.
The project currently uses the us-east-1 AWS region.
All project code should be backed up to GitHub regularly.
Future Deployment Steps

The final version of this guide will later include:

Lambda deployment instructions
API Gateway configuration
Frontend deployment to S3
SNS configuration
Full system deployment instructions
Production architecture setup