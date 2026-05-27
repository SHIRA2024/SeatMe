
"""
SeatMe Project
Seed Data Script

This script inserts example data into DynamoDB
for testing and development purposes.
"""
import boto3

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Tables
hosts_table = dynamodb.Table('Hosts')
events_table = dynamodb.Table('Events')
guests_table = dynamodb.Table('Guests')
tables_table = dynamodb.Table('Tables')

# ---------------- HOST ----------------
hosts_table.put_item(
    Item={
        'hostId': 'host1',
        'fullName': 'Shira Ben Artzi',
        'email': 'shira@example.com'
    }
)

print("Host added")

# ---------------- EVENT ----------------
events_table.put_item(
    Item={
        'eventId': 'event1',
        'hostId': 'host1',
        'eventName': 'Wedding Event',
        'eventDate': '2026-08-01'
    }
)

print("Event added")

# ---------------- GUESTS ----------------
guests = [
    {
        'guestId': 'guest1',
        'eventId': 'event1',
        'fullName': 'Daniel Cohen',
        'rsvpStatus': 'approved',
        'groupType': 'family'
    },
    {
        'guestId': 'guest2',
        'eventId': 'event1',
        'fullName': 'Noa Levi',
        'rsvpStatus': 'pending',
        'groupType': 'friends'
    },
    {
        'guestId': 'guest3',
        'eventId': 'event1',
        'fullName': 'Yossi Mizrahi',
        'rsvpStatus': 'declined',
        'groupType': 'work'
    }
]

for guest in guests:
    guests_table.put_item(Item=guest)

print("Guests added")

# ---------------- TABLES ----------------
tables = [
    {
        'tableId': 'table1',
        'eventId': 'event1',
        'tableNumber': 1,
        'capacity': 10
    },
    {
        'tableId': 'table2',
        'eventId': 'event1',
        'tableNumber': 2,
        'capacity': 8
    }
]

for table in tables:
    tables_table.put_item(Item=table)

print("Tables added")

print("Seed data inserted successfully!")