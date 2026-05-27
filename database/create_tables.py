"""
SeatMe Project
DynamoDB Table Creation Script

This script creates the main DynamoDB tables
used by the SeatMe system.

Created tables:
- Hosts
- Events
- Guests
- Tables
"""
import boto3

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# ---------------- HOSTS TABLE ----------------
hosts_table = dynamodb.create_table(
    TableName='Hosts',
    KeySchema=[
        {
            'AttributeName': 'hostId',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'hostId',
            'AttributeType': 'S'
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)

print("Hosts table created")

# ---------------- EVENTS TABLE ----------------
events_table = dynamodb.create_table(
    TableName='Events',
    KeySchema=[
        {
            'AttributeName': 'eventId',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'eventId',
            'AttributeType': 'S'
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)

print("Events table created")

# ---------------- GUESTS TABLE ----------------
guests_table = dynamodb.create_table(
    TableName='Guests',
    KeySchema=[
        {
            'AttributeName': 'guestId',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'guestId',
            'AttributeType': 'S'
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)

print("Guests table created")

# ---------------- TABLES TABLE ----------------
tables_table = dynamodb.create_table(
    TableName='Tables',
    KeySchema=[
        {
            'AttributeName': 'tableId',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'tableId',
            'AttributeType': 'S'
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)

print("Tables table created")

print("All tables created successfully!")