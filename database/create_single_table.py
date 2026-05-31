"""
SeatMe Project
Single DynamoDB Table Creation Script

This script creates a single DynamoDB table
that stores all entities used by the system.
"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.create_table(
    TableName='SeatMe',
    KeySchema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)

print("SeatMe table created successfully!")