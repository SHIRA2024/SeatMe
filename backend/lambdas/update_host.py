import json
import re
from datetime import datetime
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

    host_email = body.get('host_email')
    if not host_email:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required field: host_email'})
        }

    host_email = host_email.strip()

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', host_email):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid email format'})
        }

    name = body.get('name')
    event_name = body.get('event_name')
    event_date = body.get('event_date')
    event_location = body.get('event_location')

    if event_date is not None:
        try:
            datetime.strptime(event_date.strip(), '%Y-%m-%d')
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid date format, expected YYYY-MM-DD'})
            }

    update_parts = []
    attr_names = {}
    attr_values = {}

    if name is not None:
        update_parts.append('#n = :n')
        attr_names['#n'] = 'name'
        attr_values[':n'] = name.strip()

    if event_name is not None:
        update_parts.append('#en = :en')
        attr_names['#en'] = 'event_name'
        attr_values[':en'] = event_name.strip()

    if event_date is not None:
        update_parts.append('#ed = :ed')
        attr_names['#ed'] = 'event_date'
        attr_values[':ed'] = event_date.strip()

    if event_location is not None:
        update_parts.append('#el = :el')
        attr_names['#el'] = 'event_location'
        attr_values[':el'] = event_location.strip()

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
        'body': json.dumps({'message': 'Host updated'})
    }
