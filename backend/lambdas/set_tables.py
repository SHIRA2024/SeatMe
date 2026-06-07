"""
SeatMe - Configure tables
Feature: F10 (Define tables & seat capacities) - POST /tables
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

    required = ['host_email', 'tables']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'Missing required fields: {", ".join(missing)}'})
        }

    host_email = body['host_email'].strip().lower()
    tables = body['tables']

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', host_email):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid email format'})
        }

    denied = require_owner(event, host_email)
    if denied:
        return denied

    if not isinstance(tables, dict) or not tables:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'tables must be a non-empty dict of table_number: {capacity: int}'})
        }

    for table_num, info in tables.items():
        if not isinstance(info, dict) or 'capacity' not in info:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': f'Table {table_num} missing capacity'})
            }
        if not isinstance(info['capacity'], int) or info['capacity'] < 1:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': f'Table {table_num} capacity must be a positive integer'})
            }

    # Read current guests so we can clear seat assignments to removed tables.
    existing = table.get_item(Key={'email': host_email}).get('Item')
    if not existing:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Host not found'})
        }

    valid_tables = {str(k) for k in tables.keys()}
    guests = existing.get('guests', {})
    stale = [e for e, g in guests.items()
             if g.get('table') is not None and str(g['table']) not in valid_tables]

    attr_names = {'#t': 'tables'}
    attr_values = {':t': tables}
    remove_parts = []
    for i, g_email in enumerate(stale):
        gkey = f'#g{i}'
        attr_names[gkey] = g_email
        attr_names['#gt'] = 'table'
        remove_parts.append(f'guests.{gkey}.#gt')

    update_expr = 'SET #t = :t'
    if remove_parts:
        update_expr += ' REMOVE ' + ', '.join(remove_parts)

    try:
        table.update_item(
            Key={'email': host_email},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
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
        'body': json.dumps({'message': 'Tables updated', 'tables': tables})
    }
