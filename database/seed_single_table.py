"""
SeatMe Project
Seed Data Script

Inserts example host rows with nested guests
into the SeatMe DynamoDB table.
"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('SeatMe')

table.put_item(
    Item={
        'email': 'shira@example.com',
        'name': 'Shira Ben Artzi',
        'event_name': 'Wedding of Shira & Daniel',
        'event_date': '2026-08-01',
        'event_location': 'Tel Aviv',
        'guests': {
            'daniel@example.com': {
                'name': 'Daniel Cohen',
                'rsvp': 'yes',
                'table': 1,
                'category': 'family',
                'count': 2
            },
            'noa@example.com': {
                'name': 'Noa Levi',
                'rsvp': '?',
                'table': None,
                'category': 'friend',
                'count': 1
            }
        },
        'tables': {
            '1': {'capacity': 10},
            '2': {'capacity': 8},
            '3': {'capacity': 6}
        }
    }
)

print("Seed data inserted successfully!")