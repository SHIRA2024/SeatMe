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

    required = ['host_email', 'guest_email']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'Missing required fields: {", ".join(missing)}'})
        }

    host_email = body['host_email'].strip()
    guest_email = body['guest_email'].strip()
    name = body.get('name')
    guest_table = body.get('table')
    category = body.get('category')
    count = body.get('count')

    if count is not None and (not isinstance(count, int) or count < 1):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'count must be a positive integer'})
        }

    for addr in [host_email, guest_email]:
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', addr):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': f'Invalid email format: {addr}'})
            }

    update_parts = []
    attr_names = {'#gid': guest_email}
    attr_values = {}

    if name is not None:
        update_parts.append('guests.#gid.#n = :n')
        attr_names['#n'] = 'name'
        attr_values[':n'] = name

    if guest_table is not None:
        update_parts.append('guests.#gid.#t = :t')
        attr_names['#t'] = 'table'
        attr_values[':t'] = guest_table

    if category is not None:
        update_parts.append('guests.#gid.#c = :c')
        attr_names['#c'] = 'category'
        attr_values[':c'] = category

    if count is not None:
        update_parts.append('guests.#gid.#cnt = :cnt')
        attr_names['#cnt'] = 'count'
        attr_values[':cnt'] = count

    if not update_parts:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'No fields to update'})
        }

    try:
        table.update_item(
            Key={'email': host_email},
            UpdateExpression='SET ' + ', '.join(update_parts),
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
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
        'body': json.dumps({'message': 'Guest updated', 'guest_email': guest_email})
    }
