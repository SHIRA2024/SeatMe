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
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON body'})
        }

    required = ['host_email', 'guest_email', 'rsvp']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'Missing required fields: {", ".join(missing)}'})
        }

    host_email = body['host_email'].strip()
    guest_email = body['guest_email'].strip()
    rsvp = body['rsvp'].strip()

    for addr in [host_email, guest_email]:
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', addr):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid email format'})
            }

    if rsvp not in ('yes', 'no', '?'):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'rsvp must be yes, no, or ?'})
        }

    try:
        table.update_item(
            Key={'email': host_email},
            UpdateExpression='SET guests.#gid.#r = :r',
            ExpressionAttributeNames={
                '#gid': guest_email,
                '#r': 'rsvp'
            },
            ExpressionAttributeValues={':r': rsvp},
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
        'body': json.dumps({'message': 'RSVP updated', 'guest_email': guest_email, 'rsvp': rsvp})
    }
