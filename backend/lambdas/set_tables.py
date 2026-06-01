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

    required = ['host_email', 'tables']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'Missing required fields: {", ".join(missing)}'})
        }

    host_email = body['host_email'].strip()
    tables = body['tables']

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', host_email):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid email format'})
        }

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

    try:
        table.update_item(
            Key={'email': host_email},
            UpdateExpression='SET #t = :t',
            ExpressionAttributeNames={'#t': 'tables'},
            ExpressionAttributeValues={':t': tables},
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
