"""
SeatMe - Example Data Seeder
============================
Creates a demo host with 50 guests by invoking the deployed Lambda functions,
then defines tables, records RSVPs and generates a seating plan. Useful for
demos and manual testing.

Run from AWS CloudShell (after the Lambdas are deployed):
  cd SeatMe/backend/deploy
  python3 seed_example.py

Or seed as part of a full deploy:
  python3 redeploy_all.py --seed
"""

import json
import boto3

lambda_client = boto3.client('lambda', region_name='us-east-1')

HOST_EMAIL = 'demo@seatme.app'


def invoke_lambda(function_name, payload):
    response = lambda_client.invoke(
        FunctionName=f'SeatMe-{function_name}',
        InvocationType='RequestResponse',
        Payload=json.dumps({'body': json.dumps(payload)})
    )
    result = json.loads(response['Payload'].read())
    print(f'  {function_name}: {result["statusCode"]} - {json.loads(result["body"]).get("message", result["body"][:80])}')
    return result


# Clean up if host exists from previous run
print('=== Cleanup ===')
invoke_lambda('delete_host', {'email': HOST_EMAIL})

print('\n=== Creating Host ===')
invoke_lambda('add_host', {
    'name': 'Israel Israeli',
    'email': HOST_EMAIL,
    'event_name': 'Wedding of Israel & Israela',
    'event_date': '2026-09-15',
    'event_location': 'Haifa'
})

print('\n=== Adding 50 Guests ===')
guests = [
    # Family - 15 guests (some with +1)
    {'name': 'Daniel Cohen',      'guest_email': 'daniel@example.com',      'category': 'family', 'count': 2},
    {'name': 'Noa Levi',          'guest_email': 'noa@example.com',         'category': 'family', 'count': 1},
    {'name': 'Avi Shapira',       'guest_email': 'avi@example.com',         'category': 'family', 'count': 2},
    {'name': 'Tamar Goldstein',   'guest_email': 'tamar@example.com',       'category': 'family', 'count': 1},
    {'name': 'Yael Cohen',        'guest_email': 'yael@example.com',        'category': 'family', 'count': 2},
    {'name': 'Moshe Levi',        'guest_email': 'moshe@example.com',       'category': 'family', 'count': 3},
    {'name': 'Ruth Shapira',      'guest_email': 'ruth@example.com',        'category': 'family', 'count': 1},
    {'name': 'David Goldstein',   'guest_email': 'david@example.com',       'category': 'family', 'count': 3},
    {'name': 'Sara Cohen',        'guest_email': 'sara@example.com',        'category': 'family', 'count': 1},
    {'name': 'Amit Levi',         'guest_email': 'amit@example.com',        'category': 'family', 'count': 1},
    {'name': 'Rivka Shapira',     'guest_email': 'rivka@example.com',       'category': 'family', 'count': 2},
    {'name': 'Yosef Goldstein',   'guest_email': 'yosef@example.com',       'category': 'family', 'count': 1},
    {'name': 'Miriam Cohen',      'guest_email': 'miriam@example.com',      'category': 'family', 'count': 2},
    {'name': 'Eli Levi',          'guest_email': 'eli@example.com',         'category': 'family', 'count': 1},
    {'name': 'Hana Shapira',      'guest_email': 'hana@example.com',        'category': 'family', 'count': 1},

    # Friends - 20 guests (mix of counts)
    {'name': 'Eyal Mizrahi',      'guest_email': 'eyal@example.com',        'category': 'friend', 'count': 2},
    {'name': 'Maya Peretz',       'guest_email': 'maya@example.com',        'category': 'friend', 'count': 1},
    {'name': 'Oren Katz',         'guest_email': 'oren@example.com',        'category': 'friend', 'count': 2},
    {'name': 'Shira Dahan',       'guest_email': 'shira@example.com',       'category': 'friend', 'count': 1},
    {'name': 'Itay Azulay',       'guest_email': 'itay@example.com',        'category': 'friend', 'count': 1},
    {'name': 'Liora Ben David',   'guest_email': 'liora@example.com',       'category': 'friend', 'count': 3},
    {'name': 'Gal Avraham',       'guest_email': 'gal@example.com',         'category': 'friend', 'count': 1},
    {'name': 'Tomer Yosef',       'guest_email': 'tomer@example.com',       'category': 'friend', 'count': 1},
    {'name': 'Noga Friedman',     'guest_email': 'noga@example.com',        'category': 'friend', 'count': 2},
    {'name': 'Roi Haim',          'guest_email': 'roi@example.com',         'category': 'friend', 'count': 1},
    {'name': 'Dana Biton',        'guest_email': 'dana@example.com',        'category': 'friend', 'count': 1},
    {'name': 'Yuval Malka',       'guest_email': 'yuval@example.com',       'category': 'friend', 'count': 2},
    {'name': 'Keren Ohana',       'guest_email': 'keren@example.com',       'category': 'friend', 'count': 1},
    {'name': 'Nadav Gabay',       'guest_email': 'nadav@example.com',       'category': 'friend', 'count': 1},
    {'name': 'Tal Abutbul',       'guest_email': 'tal@example.com',         'category': 'friend', 'count': 1},
    {'name': 'Moran Edri',        'guest_email': 'moran@example.com',       'category': 'friend', 'count': 2},
    {'name': 'Bar Ohayon',        'guest_email': 'bar@example.com',         'category': 'friend', 'count': 1},
    {'name': 'Sapir Hadad',       'guest_email': 'sapir@example.com',       'category': 'friend', 'count': 1},
    {'name': 'Ido Amar',          'guest_email': 'ido@example.com',         'category': 'friend', 'count': 1},
    {'name': 'Yarden Segal',      'guest_email': 'yarden@example.com',      'category': 'friend', 'count': 1},

    # Work - 10 guests
    {'name': 'Shir David',        'guest_email': 'shir@example.com',        'category': 'work', 'count': 1},
    {'name': 'Lior Alon',         'guest_email': 'lior@example.com',        'category': 'work', 'count': 2},
    {'name': 'Rotem Bar',         'guest_email': 'rotem@example.com',       'category': 'work', 'count': 1},
    {'name': 'Alon Stern',        'guest_email': 'alon@example.com',        'category': 'work', 'count': 1},
    {'name': 'Nir Barak',         'guest_email': 'nir@example.com',         'category': 'work', 'count': 3},
    {'name': 'Mika Rosen',        'guest_email': 'mika@example.com',        'category': 'work', 'count': 1},
    {'name': 'Ofir Naor',         'guest_email': 'ofir@example.com',        'category': 'work', 'count': 1},
    {'name': 'Guy Shalem',        'guest_email': 'guy@example.com',         'category': 'work', 'count': 1},
    {'name': 'Roni Tzur',         'guest_email': 'roni@example.com',        'category': 'work', 'count': 1},
    {'name': 'Noam Stein',        'guest_email': 'noam@example.com',        'category': 'work', 'count': 1},

    # Neighbors - 5 guests
    {'name': 'Rina Mor',          'guest_email': 'rina@example.com',        'category': 'neighbor', 'count': 2},
    {'name': 'Kobi Tal',          'guest_email': 'kobi@example.com',        'category': 'neighbor', 'count': 1},
    {'name': 'Efrat Golan',       'guest_email': 'efrat@example.com',       'category': 'neighbor', 'count': 3},
    {'name': 'Dor Almog',         'guest_email': 'dor@example.com',         'category': 'neighbor', 'count': 1},
    {'name': 'Sivan Paz',         'guest_email': 'sivan@example.com',       'category': 'neighbor', 'count': 1},
]

for guest in guests:
    invoke_lambda('add_guest', {'host_email': HOST_EMAIL, **guest})

print('\n=== RSVP Guests ===')
# 42 yes, 5 no, 3 unknown
rsvps = [
    # Family - all yes
    ('daniel@example.com', 'yes'), ('noa@example.com', 'yes'), ('avi@example.com', 'yes'),
    ('tamar@example.com', 'yes'), ('yael@example.com', 'yes'), ('moshe@example.com', 'yes'),
    ('ruth@example.com', 'yes'), ('david@example.com', 'yes'), ('sara@example.com', 'yes'),
    ('amit@example.com', 'yes'), ('rivka@example.com', 'yes'), ('yosef@example.com', 'yes'),
    ('miriam@example.com', 'yes'), ('eli@example.com', 'yes'), ('hana@example.com', 'yes'),
    # Friends - 17 yes, 3 no
    ('eyal@example.com', 'yes'), ('maya@example.com', 'yes'), ('oren@example.com', 'yes'),
    ('shira@example.com', 'yes'), ('itay@example.com', 'yes'), ('liora@example.com', 'yes'),
    ('gal@example.com', 'yes'), ('tomer@example.com', 'yes'), ('noga@example.com', 'yes'),
    ('roi@example.com', 'yes'), ('dana@example.com', 'yes'), ('yuval@example.com', 'yes'),
    ('keren@example.com', 'yes'), ('nadav@example.com', 'yes'), ('tal@example.com', 'yes'),
    ('moran@example.com', 'yes'), ('bar@example.com', 'yes'),
    ('sapir@example.com', 'no'), ('ido@example.com', 'no'), ('yarden@example.com', 'no'),
    # Work - 7 yes, 3 unknown
    ('shir@example.com', 'yes'), ('lior@example.com', 'yes'), ('rotem@example.com', 'yes'),
    ('alon@example.com', 'yes'), ('nir@example.com', 'yes'), ('mika@example.com', 'yes'),
    ('ofir@example.com', 'yes'),
    ('guy@example.com', '?'), ('roni@example.com', '?'), ('noam@example.com', '?'),
    # Neighbors - 3 yes, 2 no
    ('rina@example.com', 'yes'), ('kobi@example.com', 'yes'), ('efrat@example.com', 'yes'),
    ('dor@example.com', 'no'), ('sivan@example.com', 'no'),
]

for guest_email, rsvp in rsvps:
    invoke_lambda('rsvp_guest', {'host_email': HOST_EMAIL, 'guest_email': guest_email, 'rsvp': rsvp})

print('\n=== Setting Tables ===')
table_caps = {
    '1':  {'capacity': 10},
    '2':  {'capacity': 10},
    '3':  {'capacity': 10},
    '4':  {'capacity': 8},
    '5':  {'capacity': 8},
    '6':  {'capacity': 8},
    '7':  {'capacity': 6},
    '8':  {'capacity': 6},
}
invoke_lambda('set_tables', {
    'host_email': HOST_EMAIL,
    'tables': table_caps
})

print('\n=== Generating Seating ===')
invoke_lambda('generate_seating', {'host_email': HOST_EMAIL})

print('\n=== Final Guest List ===')
response = lambda_client.invoke(
    FunctionName='SeatMe-get_guests',
    InvocationType='RequestResponse',
    Payload=json.dumps({'queryStringParameters': {'host_email': HOST_EMAIL}})
)
result = json.loads(response['Payload'].read())
guests_data = json.loads(result['body']).get('guests', {})

print(f'\n  {"Guest Email":<25} {"Name":<22} {"RSVP":<6} {"Count":<7} {"Table":<7} {"Category"}')
print(f'  {"-"*25} {"-"*22} {"-"*6} {"-"*7} {"-"*7} {"-"*10}')
for email, info in sorted(guests_data.items(), key=lambda x: (int(x[1]['table']) if x[1].get('table') is not None else 99, x[0])):
    cnt = int(info.get('count', 1))
    print(f'  {email:<25} {info["name"]:<22} {info["rsvp"]:<6} {cnt:<7} {str(info.get("table") or "-"):<7} {info.get("category", "")}')

# Summary
yes_count = sum(1 for g in guests_data.values() if g['rsvp'] == 'yes')
no_count = sum(1 for g in guests_data.values() if g['rsvp'] == 'no')
unknown_count = sum(1 for g in guests_data.values() if g['rsvp'] == '?')
seated = sum(1 for g in guests_data.values() if g.get('table') is not None)
total_people = sum(int(g.get('count', 1)) for g in guests_data.values() if g['rsvp'] == 'yes')

print(f'\n  Summary: {len(guests_data)} invites | {yes_count} yes ({total_people} people) | {no_count} no | {unknown_count} unknown | {seated} seated')

# Table diagram
print('\n=== Seating Diagram ===\n')
tables_map = {}
for email, info in guests_data.items():
    t = info.get('table')
    if t is not None:
        tables_map.setdefault(int(t), []).append(info)

for tnum in sorted(tables_map.keys()):
    guests_at_table = tables_map[tnum]
    cap = int(table_caps.get(str(tnum), {}).get('capacity', len(guests_at_table)))
    people = sum(int(g.get('count', 1)) for g in guests_at_table)
    cats = set(g.get('category', '') for g in guests_at_table)
    cat_label = ', '.join(sorted(cats)) if cats else ''

    print(f'  ┌{"─" * 40}┐')
    print(f'  │  Table {tnum:<3} ({people}/{cap} seats) [{cat_label}]')
    print(f'  ├{"─" * 40}┤')
    for g in sorted(guests_at_table, key=lambda x: x['name']):
        cat = g.get('category', '')
        cnt = int(g.get('count', 1))
        print(f'  │  • {g["name"]:<22} x{cnt} ({cat:<8}) │')
    for _ in range(cap - people):
        print(f'  │    (empty seat)                      │')
    print(f'  └{"─" * 40}┘')
    print()

print('Done!')
