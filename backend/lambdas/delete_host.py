"""
SeatMe - Delete event
Feature: F09 (Delete event and all its guests) - DELETE /hosts
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

    email = body.get('email')
    if not email:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required field: email'})
        }

    email = email.strip().lower()

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid email format'})
        }

    denied = require_owner(event, email)
    if denied:
        return denied

    try:
        table.delete_item(
            Key={'email': email},
            ConditionExpression='attribute_exists(email)'
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Host not found'})
            }
        raise

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Host deleted', 'email': email})
    }
