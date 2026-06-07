"""
SeatMe - Create event (host)
Feature: F06 (Create event) - POST /hosts
"""

import json
import re
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from _common import require_owner

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SeatMe')


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON body'})
        }

    required = ['name', 'email', 'event_name', 'event_date', 'event_location']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'Missing required fields: {", ".join(missing)}'})
        }

    name = body['name'].strip()
    email = body['email'].strip().lower()
    event_name = body['event_name'].strip()
    event_date = body['event_date'].strip()
    event_location = body['event_location'].strip()

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid email format'})
        }

    denied = require_owner(event, email)
    if denied:
        return denied

    try:
        datetime.strptime(event_date, '%Y-%m-%d')
    except ValueError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid date format, expected YYYY-MM-DD'})
        }

    try:
        table.put_item(
            Item={
                'email': email,
                'name': name,
                'event_name': event_name,
                'event_date': event_date,
                'event_location': event_location,
                'guests': {},
                'tables': {},
                'categories': ['Family', 'Friends', 'Work', 'Other']
            },
            ConditionExpression='attribute_not_exists(email)'
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 409,
                'body': json.dumps({'message': 'Host with this email already exists'})
            }
        raise

    return {
        'statusCode': 201,
        'body': json.dumps({
            'email': email,
            'name': name,
            'event_name': event_name,
            'event_date': event_date,
            'event_location': event_location
        })
    }
