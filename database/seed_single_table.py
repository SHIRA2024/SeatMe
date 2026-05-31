"""
SeatMe Project
Single Table Seed Data Script

This script inserts example data into the
SeatMe DynamoDB table.
"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('SeatMe')

# Host
table.put_item(
    Item={
        'id': 'host1',
        'entityType': 'HOST',
        'fullName': 'Shira Ben Artzi',
        'email': 'shira@example.com'
    }
)

# Event
table.put_item(
    Item={
        'id': 'event1',
        'entityType': 'EVENT',
        'hostId': 'host1',
        'eventName': 'Wedding Event',
        'eventDate': '2026-08-01'
    }
)

# Guests
table.put_item(
    Item={
        'id': 'guest1',
        'entityType': 'GUEST',
        'eventId': 'event1',
        'fullName': 'Daniel Cohen',
        'rsvpStatus': 'approved'
    }
)

table.put_item(
    Item={
        'id': 'guest2',
        'entityType': 'GUEST',
        'eventId': 'event1',
        'fullName': 'Noa Levi',
        'rsvpStatus': 'pending'
    }
)

# Tables
table.put_item(
    Item={
        'id': 'table1',
        'entityType': 'TABLE',
        'eventId': 'event1',
        'tableNumber': 1,
        'capacity': 10
    }
)

print("Seed data inserted successfully!")