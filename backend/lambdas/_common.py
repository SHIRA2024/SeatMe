"""
SeatMe - shared Lambda helpers
==============================
Server-side authorization used by the write endpoints (create/update/delete
host & guest, tables, seating, invitations). It is bundled into every Lambda
zip by setup_aws.zip_lambda, so handlers can simply `from _common import
require_owner`.

Authorization rule for a write request:
  * Direct AWS SDK invocations (e.g. the seed script) are trusted and allowed -
    only a principal that already holds lambda:InvokeFunction can make them, and
    API Gateway requests always carry a requestContext, so they never qualify.
  * Otherwise the caller must present a valid Cognito access token AND either
      - own the resource (their email == the event's host email), or
      - belong to the 'admin' group.

Public endpoints (get_host, get_guests, rsvp_guest) do not import this module:
the public RSVP page and the shareable read-only preview link rely on them.
"""

import json
import boto3
from botocore.exceptions import ClientError

REGION = 'us-east-1'
POOL_NAME = 'SeatMe-Users'
ADMIN_GROUP = 'admin'

cognito = boto3.client('cognito-idp', region_name=REGION)

_pool_id_cache = None


def _resp(status, message):
    return {'statusCode': status, 'body': json.dumps({'message': message})}


def _is_direct_invoke(event):
    """API Gateway (HTTP API, payload v2) always sets requestContext. A bare
    event without it comes from a trusted direct SDK invoke (e.g. the seeder)."""
    return not isinstance(event, dict) or 'requestContext' not in event


def _bearer_token(event):
    """Extract the bearer token from the Authorization header (case-insensitive)."""
    headers = {k.lower(): v for k, v in (event.get('headers') or {}).items()}
    raw = headers.get('authorization', '') or ''
    return raw[7:].strip() if raw.lower().startswith('bearer ') else raw.strip()


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


def _is_admin(username):
    """True if the Cognito user belongs to the admin group."""
    pool_id = _find_pool_id()
    if not pool_id or not username:
        return False
    try:
        groups = cognito.admin_list_groups_for_user(UserPoolId=pool_id, Username=username)
        return ADMIN_GROUP in {g['GroupName'] for g in groups.get('Groups', [])}
    except ClientError:
        return False


def require_owner(event, resource_email):
    """Return None if the caller may modify resource_email, else an error response
    ({'statusCode': 401/403, ...}) the handler should return immediately."""
    if _is_direct_invoke(event):
        return None  # trusted internal/SDK invoke (e.g. seed_example.py)

    token = _bearer_token(event)
    if not token:
        return _resp(401, 'Sign in to make changes')

    # GetUser validates the access token (signature + expiry) for us.
    try:
        user = cognito.get_user(AccessToken=token)
    except ClientError:
        return _resp(401, 'Your session has expired - please sign in again')

    attrs = {a['Name']: a['Value'] for a in user.get('UserAttributes', [])}
    caller = (attrs.get('email') or user.get('Username') or '').strip().lower()
    target = (resource_email or '').strip().lower()

    if caller and caller == target:
        return None
    if _is_admin(user.get('Username')):
        return None
    return _resp(403, 'You can only manage your own event')
