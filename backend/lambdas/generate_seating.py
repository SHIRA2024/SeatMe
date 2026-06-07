"""
SeatMe - Automatic seating
Feature: F16 (Auto-assign confirmed guests to tables) - POST /seating
"""

import json
import re
import boto3
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

    host_email = body.get('host_email')
    if not host_email:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required field: host_email'})
        }

    host_email = host_email.strip().lower()

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', host_email):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid email format'})
        }

    denied = require_owner(event, host_email)
    if denied:
        return denied

    response = table.get_item(Key={'email': host_email})

    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Host not found'})
        }

    guests = response['Item'].get('guests', {})
    tables = response['Item'].get('tables', {})

    if not tables:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'No tables defined for this host'})
        }

    # Only seat guests who RSVP'd yes
    confirmed = {email: g for email, g in guests.items() if g.get('rsvp') == 'yes'}

    # Check total capacity vs total people (counting +guests)
    total_capacity = sum(int(t.get('capacity', 0)) for t in tables.values())
    total_people = sum(int(g.get('count', 1)) for g in confirmed.values())
    if total_people > total_capacity:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Not enough seats',
                'total_people': total_people,
                'total_capacity': total_capacity
            })
        }

    # Group confirmed guests by category
    categories = {}
    for email, guest in confirmed.items():
        cat = guest.get('category', '') or ''
        categories.setdefault(cat, []).append(email)

    # Sort categories by group size descending (seat largest groups first)
    sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

    # Build table list sorted by number, track remaining capacity
    seats = []
    for tnum, tinfo in sorted(tables.items(), key=lambda x: int(x[0])):
        seats.append({'num': int(tnum), 'capacity': int(tinfo.get('capacity', 0)), 'seated': 0})

    assignments = {}

    for category, guest_list in sorted_cats:
        remaining = list(guest_list)

        while remaining:
            # Find table with most free seats
            best = None
            best_free = 0
            for t in seats:
                free = t['capacity'] - t['seated']
                if free > best_free:
                    best = t
                    best_free = free

            if best is None or best_free == 0:
                break

            # Seat as many from this category as possible at this table
            still_remaining = []
            for email in remaining:
                guest_count = int(confirmed[email].get('count', 1))
                free = best['capacity'] - best['seated']
                if guest_count <= free:
                    assignments[email] = best['num']
                    best['seated'] += guest_count
                else:
                    still_remaining.append(email)
            if len(still_remaining) == len(remaining):
                # No one could fit, try next table
                break
            remaining = still_remaining

    # Persist: assign tables for seated guests and clear any stale assignments
    # (guests previously seated who are no longer confirmed or no longer fit).
    attr_names = {'#t': 'table'}
    attr_values = {}
    set_parts = []
    remove_parts = []

    idx = 0
    for guest_email, tbl in assignments.items():
        gid_key = f'#g{idx}'
        tbl_key = f':t{idx}'
        attr_names[gid_key] = guest_email
        attr_values[tbl_key] = tbl
        set_parts.append(f'guests.{gid_key}.#t = {tbl_key}')
        idx += 1

    for guest_email, g in guests.items():
        if g.get('table') is not None and guest_email not in assignments:
            gid_key = f'#g{idx}'
            attr_names[gid_key] = guest_email
            remove_parts.append(f'guests.{gid_key}.#t')
            idx += 1

    update_expr = ''
    if set_parts:
        update_expr = 'SET ' + ', '.join(set_parts)
    if remove_parts:
        update_expr += (' ' if update_expr else '') + 'REMOVE ' + ', '.join(remove_parts)

    if update_expr:
        kwargs = dict(
            Key={'email': host_email},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=attr_names,
        )
        if attr_values:
            kwargs['ExpressionAttributeValues'] = attr_values
        table.update_item(**kwargs)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Seating generated',
            'total_guests_seated': len(assignments),
            'assignments': assignments
        })
    }
