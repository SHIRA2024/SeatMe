import json
import boto3
from botocore.exceptions import ClientError
from urllib.parse import quote

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

table = dynamodb.Table('SeatMe')

TOPIC_ARN = 'arn:aws:sns:us-east-1:637423276982:SeatMe-Invitations'
SITE_URL = 'http://seatme-637423276982.s3-website-us-east-1.amazonaws.com'


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON body'})
        }

    host_email = body.get('host_email', '').strip()
    guest_email = body.get('guest_email', '').strip()
    custom_message = body.get('message', '').strip()

    subscriptions = sns.list_subscriptions_by_topic(TopicArn=TOPIC_ARN)

    is_confirmed = any(
        sub.get('Endpoint') == guest_email and
        sub.get('Protocol') == 'email' and
        sub.get('SubscriptionArn') != 'PendingConfirmation'
        for sub in subscriptions.get('Subscriptions', [])
    )

    if not is_confirmed:
        sns.subscribe(
            TopicArn=TOPIC_ARN,
            Protocol='email',
            Endpoint=guest_email
        )

        return {
            'statusCode': 202,
            'body': json.dumps({
                'message': 'Guest must confirm SNS subscription before receiving invitations',
                'guest_email': guest_email
            })
        }

    if not host_email or not guest_email:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'host_email and guest_email are required'})
        }

    try:
        response = table.get_item(Key={'email': host_email})
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Failed to read host data', 'error': str(e)})
        }

    host = response.get('Item')
    if not host:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Host not found'})
        }

    guests = host.get('guests', {})
    guest = guests.get(guest_email)

    if not guest:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Guest not found'})
        }

    guest_name = guest.get('name', guest_email)
    event_name = host.get('event_name', 'your event')
    event_date = host.get('event_date', '')
    event_location = host.get('event_location', '')

    invite_link = (
        f"{SITE_URL}/SCREEN~2.HTM"
        f"?host={quote(host_email)}&guest={quote(guest_email)}"
    )

    message = custom_message if custom_message else f"""
    Hello {guest_name},

    You are invited to: {event_name}

    Date: {event_date}
    Location: {event_location}

    Please confirm your RSVP using this link:
    {invite_link}

    SeatMe
    """

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject='SeatMe Invitation',
        Message=message
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Invitation sent successfully',
            'guest_email': guest_email,
            'invite_link': invite_link
        })
    }