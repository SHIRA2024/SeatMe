"""
SeatMe - Update guest
Feature: F13 (Update guest details / assign seat) - PUT /guests
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
        return {'statusCode': 400, 'body': json.dumps({'message': 'Invalid JSON body'})}

    missing = [f for f in ['host_email', 'guest_email'] if not body.get(f)]
    if missing:
        return {'statusCode': 400, 'body': json.dumps({'message': f'Missing required fields: {", ".join(missing)}'})}

    host_email  = body['host_email'].strip().lower()
    guest_email = body['guest_email'].strip().lower()

    for addr in [host_email, guest_email]:
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', addr):
            return {'statusCode': 400, 'body': json.dumps({'message': f'Invalid email format: {addr}'})}

    denied = require_owner(event, host_email)
    if denied:
        return denied

    count = body.get('count')
    if count is not None and (not isinstance(count, int) or count < 1 or count > MAX_COUNT):
        return {'statusCode': 400, 'body': json.dumps({'message': f'count must be between 1 and {MAX_COUNT}'})}

    set_parts    = []
    remove_parts = []
    attr_names   = {'#gid': guest_email}
    attr_values  = {}

    # Simple scalar fields – only update if key exists in body
    for field, alias, val_key, attr in [
        ('name',     '#n',  ':n',  'name'),
        ('category', '#c',  ':c',  'category'),
        ('rsvp',     '#r',  ':r',  'rsvp'),
    ]:
        if field in body and body[field] is not None:
            set_parts.append(f'guests.#gid.{alias} = {val_key}')
            attr_names[alias] = attr
            attr_values[val_key] = body[field]

    # count (validated above)
    if count is not None:
        set_parts.append('guests.#gid.#cnt = :cnt')
        attr_names['#cnt'] = 'count'
        attr_values[':cnt'] = count

    # table: null → REMOVE (clear assignment), value → SET
    if 'table' in body:
        attr_names['#t'] = 'table'
        if body['table'] is None:
            remove_parts.append('guests.#gid.#t')
        else:
            set_parts.append('guests.#gid.#t = :t')
            attr_values[':t'] = body['table']

    if not set_parts and not remove_parts:
        return {'statusCode': 400, 'body': json.dumps({'message': 'No fields to update'})}

    expr = ('SET ' + ', '.join(set_parts) if set_parts else '') + \
           ((' ' if set_parts else '') + 'REMOVE ' + ', '.join(remove_parts) if remove_parts else '')

    kwargs = dict(
        Key={'email': host_email},
        UpdateExpression=expr,
        ExpressionAttributeNames=attr_names,
        ConditionExpression='attribute_exists(guests.#gid)',
    )
    if attr_values:
        kwargs['ExpressionAttributeValues'] = attr_values

    try:
        table.update_item(**kwargs)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {'statusCode': 404, 'body': json.dumps({'message': 'Host or guest not found'})}
        raise

    return {'statusCode': 200, 'body': json.dumps({'message': 'Guest updated', 'guest_email': guest_email})}
