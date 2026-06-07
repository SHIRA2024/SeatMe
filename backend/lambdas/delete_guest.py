"""
SeatMe - Delete guest
Feature: F14 (Remove a guest from an event) - DELETE /guests
"""

import json
import re
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

    required = ['host_email', 'guest_email']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'Missing required fields: {", ".join(missing)}'})
        }

    host_email = body['host_email'].strip().lower()
    guest_email = body['guest_email'].strip().lower()

    for addr in [host_email, guest_email]:
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', addr):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid email format'})
            }

    denied = require_owner(event, host_email)
    if denied:
        return denied

    try:
        table.update_item(
            Key={'email': host_email},
            UpdateExpression='REMOVE guests.#gid',
            ExpressionAttributeNames={'#gid': guest_email},
            ConditionExpression='attribute_exists(guests.#gid)'
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Host or guest not found'})
            }
        raise

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Guest deleted', 'guest_email': guest_email})
    }
