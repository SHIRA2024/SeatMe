"""
SeatMe - list_hosts (admin only)
================================
Feature: F18 (Admin - list & oversee all events)

Returns every host/event in the system. This is the privileged endpoint that
separates the two permission groups: only members of the Cognito 'admin' group
may call it. Enforcement is done server-side with boto3 alone (no extra deps):

  1. Validate the caller's Cognito ACCESS token via cognito-idp GetUser
     (Cognito rejects missing/expired/forged tokens).
  2. Confirm the user belongs to the 'admin' group via AdminListGroupsForUser.

Non-admin hosts receive 403, so they cannot enumerate other events.
"""

import json
import boto3
from botocore.exceptions import ClientError

REGION = 'us-east-1'
POOL_NAME = 'SeatMe-Users'
ADMIN_GROUP = 'admin'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table('SeatMe')
cognito = boto3.client('cognito-idp', region_name=REGION)

_pool_id_cache = None


def _find_pool_id():
    """Resolve the SeatMe user pool id by name (cached per warm container)."""
    global _pool_id_cache
    if _pool_id_cache:
        return _pool_id_cache
    kwargs = {'MaxResults': 60}
    while True:
        resp = cognito.list_user_pools(**kwargs)
        for pool in resp.get('UserPools', []):
            if pool['Name'] == POOL_NAME:
                _pool_id_cache = pool['Id']
                return _pool_id_cache
        token = resp.get('NextToken')
        if not token:
            return None
        kwargs['NextToken'] = token


def _bearer_token(event):
    """Extract the bearer token from the Authorization header (case-insensitive)."""
    headers = {k.lower(): v for k, v in (event.get('headers') or {}).items()}
    raw = headers.get('authorization', '')
    return raw[7:].strip() if raw.lower().startswith('bearer ') else raw.strip()


def _require_admin(event):
    """Return None if the caller is a valid admin, else an error response."""
    token = _bearer_token(event)
    if not token:
        return {'statusCode': 401, 'body': json.dumps({'message': 'Missing access token'})}

    # GetUser validates the access token (signature + expiry) for us.
    try:
        user = cognito.get_user(AccessToken=token)
    except ClientError:
        return {'statusCode': 401, 'body': json.dumps({'message': 'Invalid or expired session'})}

    pool_id = _find_pool_id()
    if not pool_id:
        return {'statusCode': 500, 'body': json.dumps({'message': 'User pool not found'})}

    groups = cognito.admin_list_groups_for_user(UserPoolId=pool_id, Username=user['Username'])
    names = {g['GroupName'] for g in groups.get('Groups', [])}
    if ADMIN_GROUP not in names:
        return {'statusCode': 403, 'body': json.dumps({'message': 'Admin privileges required'})}
    return None


def lambda_handler(event, context):
    denied = _require_admin(event)
    if denied:
        return denied

    hosts = []
    scan_kwargs = {}
    while True:
        resp = table.scan(**scan_kwargs)
        for item in resp.get('Items', []):
            hosts.append({
                'email': item.get('email'),
                'name': item.get('name'),
                'event_name': item.get('event_name'),
                'event_date': item.get('event_date'),
                'event_location': item.get('event_location'),
                'guest_count': len(item.get('guests', {})),
            })
        if 'LastEvaluatedKey' not in resp:
            break
        scan_kwargs['ExclusiveStartKey'] = resp['LastEvaluatedKey']

    hosts.sort(key=lambda h: (h.get('event_date') or '', h.get('email') or ''))
    return {
        'statusCode': 200,
        'body': json.dumps({'hosts': hosts, 'total': len(hosts)}, default=str),
    }
