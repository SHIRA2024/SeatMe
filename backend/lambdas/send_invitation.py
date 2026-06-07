"""
SeatMe - Send Invitations (email via Amazon SNS)
================================================
Feature: F17 (Send invitations - one guest or all) - POST /invitations/send

Emails guests an invitation with their personal RSVP link.

POST /invitations/send
  { "host_email": "...", "site_url": "https://...",
    "guest_email": "..."   (optional - omit to invite ALL guests),
    "message": "..."       (optional - custom text) }

SNS has no "email a single address" API, so each guest is subscribed to the
shared SeatMe-Invitations topic with a per-guest filter policy; a publish that
carries that guest's email attribute then reaches only that guest. Guests must
click "Confirm subscription" in the first email AWS sends them before any
invitation can be delivered - the response reports who is still pending.
"""

import json
import boto3
from botocore.exceptions import ClientError
from urllib.parse import quote

from _common import require_owner

REGION = 'us-east-1'
TOPIC_NAME = 'SeatMe-Invitations'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)
table = dynamodb.Table('SeatMe')


def _resp(status, body):
    return {'statusCode': status, 'body': json.dumps(body, default=str)}


def get_topic_arn():
    """Idempotently return the topic ARN (creates the topic if missing)."""
    return sns.create_topic(Name=TOPIC_NAME)['TopicArn']


def list_email_subscriptions(topic_arn):
    """email -> SubscriptionArn ('PendingConfirmation' until the guest confirms)."""
    subs, token = {}, None
    while True:
        kwargs = {'TopicArn': topic_arn}
        if token:
            kwargs['NextToken'] = token
        resp = sns.list_subscriptions_by_topic(**kwargs)
        for s in resp.get('Subscriptions', []):
            if s.get('Protocol') == 'email':
                subs[s.get('Endpoint')] = s.get('SubscriptionArn')
        token = resp.get('NextToken')
        if not token:
            return subs


def ensure_subscription(topic_arn, guest_email, subs):
    """'confirmed' if ready to receive, else 'pending' (subscribing if brand new)."""
    arn = subs.get(guest_email)
    if arn and arn != 'PendingConfirmation':
        return 'confirmed'
    if not arn:
        sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=guest_email,
            Attributes={'FilterPolicy': json.dumps({'guest_email': [guest_email]})},
            ReturnSubscriptionArn=True,
        )
        subs[guest_email] = 'PendingConfirmation'
    return 'pending'


def build_message(host, host_email, guest_email, guest, site_url, custom_message):
    guest_name = guest.get('name', guest_email)
    event_name = host.get('event_name', 'our event')
    link = ''
    if site_url:
        link = (f"{site_url.rstrip('/')}/rsvp.html"
                f"?host={quote(host_email)}&guest={quote(guest_email)}")

    if custom_message:
        return custom_message + (f"\n\nRSVP here:\n{link}" if link else '')

    lines = [f"Hello {guest_name},", "", f"You're invited to: {event_name}"]
    if host.get('event_date'):
        lines.append(f"Date: {host['event_date']}")
    if host.get('event_location'):
        lines.append(f"Location: {host['event_location']}")
    if link:
        lines += ["", "Please confirm your RSVP here:", link]
    lines += ["", "- SeatMe"]
    return "\n".join(lines)


def send_to_guest(topic_arn, host, host_email, guest_email, guest, site_url, custom_message, subs):
    if ensure_subscription(topic_arn, guest_email, subs) == 'pending':
        return 'pending'
    sns.publish(
        TopicArn=topic_arn,
        Subject='SeatMe Invitation',
        Message=build_message(host, host_email, guest_email, guest, site_url, custom_message),
        MessageAttributes={
            'guest_email': {'DataType': 'String', 'StringValue': guest_email}
        },
    )
    return 'sent'


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return _resp(400, {'message': 'Invalid JSON body'})

    host_email = body.get('host_email', '').strip().lower()
    guest_email = body.get('guest_email', '').strip().lower()
    custom_message = body.get('message', '').strip()
    site_url = body.get('site_url', '').strip()

    if not host_email:
        return _resp(400, {'message': 'host_email is required'})

    denied = require_owner(event, host_email)
    if denied:
        return denied

    try:
        host = table.get_item(Key={'email': host_email}).get('Item')
    except ClientError as e:
        print(f'send_invitation: failed to read host data: {e}')
        return _resp(500, {'message': 'Failed to read host data'})
    if not host:
        return _resp(404, {'message': 'Host not found'})

    guests = host.get('guests', {})
    if not guests:
        return _resp(404, {'message': 'No guests to invite yet'})

    try:
        topic_arn = get_topic_arn()
        subs = list_email_subscriptions(topic_arn)
    except ClientError as e:
        print(f'send_invitation: email service unavailable: {e}')
        return _resp(500, {'message': 'Email service unavailable'})

    # -- Single guest --
    if guest_email:
        guest = guests.get(guest_email)
        if not guest:
            return _resp(404, {'message': 'Guest not found'})
        try:
            status = send_to_guest(topic_arn, host, host_email, guest_email, guest,
                                   site_url, custom_message, subs)
        except ClientError as e:
            print(f'send_invitation: could not send invitation: {e}')
            return _resp(500, {'message': 'Could not send invitation'})
        if status == 'pending':
            return _resp(202, {
                'message': 'Confirmation email sent - the guest must confirm before invitations arrive.',
                'guest_email': guest_email,
                'status': 'pending',
            })
        return _resp(200, {'message': 'Invitation sent', 'guest_email': guest_email, 'status': 'sent'})

    # -- All guests --
    sent, pending, failed = [], [], []
    for g_email, guest in guests.items():
        try:
            status = send_to_guest(topic_arn, host, host_email, g_email, guest,
                                   site_url, custom_message, subs)
            (sent if status == 'sent' else pending).append(g_email)
        except ClientError:
            failed.append(g_email)

    return _resp(200, {
        'message': f'{len(sent)} sent, {len(pending)} awaiting confirmation'
                   + (f', {len(failed)} failed' if failed else ''),
        'sent': sent,
        'pending': pending,
        'failed': failed,
    })