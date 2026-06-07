"""
SeatMe - Guest RSVP (public)
Feature: F15 (Guest responds via personal link) - POST /guests/rsvp
"""

import json
import re
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SeatMe')


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid JSON body'})}

    missing = [f for f in ['host_email', 'guest_email', 'rsvp'] if not body.get(f)]
    if missing:
        return {'statusCode': 400, 'body': json.dumps({'message': f'Missing required fields: {", ".join(missing)}'})}

    host_email  = body['host_email'].strip().lower()
    guest_email = body['guest_email'].strip().lower()
    rsvp        = body['rsvp'].strip()

    for addr in [host_email, guest_email]:
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', addr):
            return {'statusCode': 400, 'body': json.dumps({'message': f'Invalid email format: {addr}'})}

    if rsvp not in ('yes', 'no', '?'):
        return {'statusCode': 400, 'body': json.dumps({'message': 'rsvp must be yes, no, or ?'})}

    count = body.get('count')
    if count is not None:
        try:
            count = int(count)
            if count < 1:
                count = 1
        except (TypeError, ValueError):
            count = None

    song = body.get('song', '').strip() if body.get('song') else None

    # Build update expression
    set_parts   = ['guests.#gid.#r = :r']
    attr_names  = {'#gid': guest_email, '#r': 'rsvp'}
    attr_values = {':r': rsvp}

    if count is not None:
        set_parts.append('guests.#gid.#cnt = :cnt')
        attr_names['#cnt'] = 'count'
        attr_values[':cnt'] = count

    if song:
        set_parts.append('guests.#gid.#s = :s')
        attr_names['#s'] = 'song'
        attr_values[':s'] = song

    try:
        table.update_item(
            Key={'email': host_email},
            UpdateExpression='SET ' + ', '.join(set_parts),
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
            ConditionExpression='attribute_exists(guests.#gid)'
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {'statusCode': 404, 'body': json.dumps({'message': 'Host or guest not found'})}
        raise

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'RSVP updated', 'guest_email': guest_email, 'rsvp': rsvp})
    }
