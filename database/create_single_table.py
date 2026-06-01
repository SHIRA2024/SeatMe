"""
SeatMe Project
DynamoDB Table Creation Script

Each row represents a host with nested guests.
Schema:
  email (str) - partition key
  name (str)
  guests (map) - { guestId: { name, email, rsvp, table } }
"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.create_table(
    TableName='SeatMe',
    KeySchema=[
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)

print("SeatMe table created successfully!")