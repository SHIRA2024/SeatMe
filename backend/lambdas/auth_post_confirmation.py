"""
SeatMe - Cognito Post-Confirmation trigger
Feature: F20 (auto-assign new sign-ups to the 'host' permission group)

Cognito invokes this function right after a user confirms their sign-up. It adds
the new user to the 'host' group so every self-service account belongs to an
explicit permission group (the admin group is assigned separately). Failures are
swallowed so a transient error can never block a user's sign-up.
"""

import boto3

REGION = 'us-east-1'
HOST_GROUP = 'host'

cognito = boto3.client('cognito-idp', region_name=REGION)


def lambda_handler(event, context):
    # Only act on a real sign-up confirmation (not password-reset confirmations).
    if event.get('triggerSource') == 'PostConfirmation_ConfirmSignUp':
        try:
            cognito.admin_add_user_to_group(
                UserPoolId=event['userPoolId'],
                Username=event['userName'],
                GroupName=HOST_GROUP,
            )
        except Exception as exc:  # never fail the sign-up because of grouping
            print(f"Could not add {event.get('userName')} to '{HOST_GROUP}': {exc}")
    # Cognito triggers must return the event unchanged.
    return event
