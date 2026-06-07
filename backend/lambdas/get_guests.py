"""
SeatMe - List guests
Feature: F12 (List all guests of an event) - GET /guests
"""

import json
import re
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SeatMe')


def lambda_handler(event, context):
    params = event.get('queryStringParameters') or {}
    host_email = params.get('host_email')

    if not host_email:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required query parameter: host_email'})
        }

    host_email = host_email.strip().lower()

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', host_email):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid email format'})
        }

    response = table.get_item(Key={'email': host_email})

    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Host not found'})
        }

    guests = response['Item'].get('guests', {})

    return {
        'statusCode': 200,
        'body': json.dumps({'guests': guests}, default=str)
    }
