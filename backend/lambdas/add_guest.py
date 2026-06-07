"""
SeatMe - Add guest
Feature: F11 (Add a guest to an event) - POST /guests
"""

import json
import re
import boto3
from botocore.exceptions import ClientError
from _common import require_owner

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SeatMe')

MAX_COUNT = 20  # upper bound on a single invite's party size


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON body'})
        }

    required = ['host_email', 'name', 'guest_email']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'Missing required fields: {", ".join(missing)}'})
        }

    host_email = body['host_email'].strip().lower()
    guest_name = body['name'].strip()
    guest_email = body['guest_email'].strip().lower()
    category = body.get('category', '').strip()
    count = body.get('count', 1)

    if not isinstance(count, int) or count < 1 or count > MAX_COUNT:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'count must be between 1 and {MAX_COUNT}'})
        }

    for addr in [host_email, guest_email]:
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', addr):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': f'Invalid email format: {addr}'})
            }

    denied = require_owner(event, host_email)
    if denied:
        return denied

    try:
        table.update_item(
            Key={'email': host_email},
            UpdateExpression='SET guests.#gid = :guest',
            ExpressionAttributeNames={'#gid': guest_email},
            ExpressionAttributeValues={
                ':guest': {
                    'name': guest_name,
                    'rsvp': '?',
                    'table': None,
                    'category': category,
                    'count': count
                }
            },
            ConditionExpression='attribute_exists(email) AND attribute_not_exists(guests.#gid)'
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 409,
                'body': json.dumps({'message': 'Host not found or guest already exists'})
            }
        raise

    return {
        'statusCode': 201,
        'body': json.dumps({
            'guest_email': guest_email,
            'name': guest_name,
            'rsvp': '?',
            'table': None,
            'category': category,
            'count': count
        })
    }
