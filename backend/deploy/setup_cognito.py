"""
SeatMe - Cognito Setup
======================
Creates (idempotently) the AWS Cognito User Pool and a public app client used
for host sign-up / sign-in. Hosts authenticate with email + password via the
USER_PASSWORD_AUTH flow directly from the browser (no client secret).

Run standalone from AWS CloudShell:

  cd SeatMe/backend/deploy
  python3 setup_cognito.py

It prints the User Pool ID and App Client ID, which the frontend needs.
redeploy_all.py calls setup_cognito() and injects those values automatically.
"""

import os
import boto3
from botocore.exceptions import ClientError

REGION = 'us-east-1'
POOL_NAME = 'SeatMe-Users'
CLIENT_NAME = 'SeatMe-Web'

# Two explicit permission groups: an 'admin' Cognito group whose members manage
# every event, and a 'host' group (the default for new sign-ups) whose members
# manage only their own event. New users are auto-added to 'host' by the
# auth_post_confirmation Lambda trigger.
ADMIN_GROUP = 'admin'
HOST_GROUP = 'host'
TRIGGER_FN_NAME = 'SeatMe-auth_post_confirmation'

# Demo accounts seeded for graders (one user of each type). Passwords satisfy the
# pool policy below (>= 8 chars). Override via environment variables if desired.
ADMIN_EMAIL = os.environ.get('SEATME_ADMIN_EMAIL', 'admin@seatme.app')
ADMIN_PASSWORD = os.environ.get('SEATME_ADMIN_PASSWORD', '12345678')
DEMO_HOST_EMAIL = os.environ.get('SEATME_HOST_EMAIL', 'demo@seatme.app')
DEMO_HOST_PASSWORD = os.environ.get('SEATME_HOST_PASSWORD', '12345678')

# Address Cognito sends verification codes "from" via Amazon SES.
# Must be a verified SES identity - this script triggers verification for you.
# Override with:  export SEATME_SENDER_EMAIL="you@yourdomain.com"
SENDER_EMAIL = os.environ.get('SEATME_SENDER_EMAIL', 'yonatang8675@gmail.com')

PASSWORD_POLICY = {
    'MinimumLength': 8,
    'RequireUppercase': False,
    'RequireLowercase': False,
    'RequireNumbers': False,
    'RequireSymbols': False,
}
ACCOUNT_RECOVERY = {'RecoveryMechanisms': [{'Priority': 1, 'Name': 'verified_email'}]}

cognito = boto3.client('cognito-idp', region_name=REGION)
ses = boto3.client('ses', region_name=REGION)


def find_pool_id():
    """Return the id of the SeatMe user pool, or None if it does not exist."""
    kwargs = {'MaxResults': 60}
    while True:
        resp = cognito.list_user_pools(**kwargs)
        for pool in resp.get('UserPools', []):
            if pool['Name'] == POOL_NAME:
                return pool['Id']
        token = resp.get('NextToken')
        if not token:
            return None
        kwargs['NextToken'] = token


def create_user_pool():
    existing = find_pool_id()
    if existing:
        print(f'  User pool already exists: {existing}')
        return existing

    resp = cognito.create_user_pool(
        PoolName=POOL_NAME,
        UsernameAttributes=['email'],          # sign in with email
        AutoVerifiedAttributes=['email'],      # email a verification code on sign-up
        Policies={'PasswordPolicy': PASSWORD_POLICY},
        AccountRecoverySetting=ACCOUNT_RECOVERY,
    )
    pool_id = resp['UserPool']['Id']
    print(f'  Created user pool: {pool_id}')
    return pool_id


def find_client_id(pool_id):
    kwargs = {'UserPoolId': pool_id, 'MaxResults': 60}
    while True:
        resp = cognito.list_user_pool_clients(**kwargs)
        for c in resp.get('UserPoolClients', []):
            if c['ClientName'] == CLIENT_NAME:
                return c['ClientId']
        token = resp.get('NextToken')
        if not token:
            return None
        kwargs['NextToken'] = token


def create_app_client(pool_id):
    existing = find_client_id(pool_id)
    if existing:
        print(f'  App client already exists: {existing}')
        return existing

    resp = cognito.create_user_pool_client(
        UserPoolId=pool_id,
        ClientName=CLIENT_NAME,
        GenerateSecret=False,                  # public client (browser)
        ExplicitAuthFlows=[
            'ALLOW_USER_PASSWORD_AUTH',
            'ALLOW_REFRESH_TOKEN_AUTH',
            'ALLOW_USER_SRP_AUTH',
        ],
        PreventUserExistenceErrors='ENABLED',
    )
    client_id = resp['UserPoolClient']['ClientId']
    print(f'  Created app client: {client_id}')
    return client_id


# ─── Email delivery via Amazon SES (optional) ──────────────────────────────
# Cognito's built-in mailer works everywhere but is rate-limited and often lands
# in spam. If this account may use SES, we send codes from SENDER_EMAIL instead.
# In restricted accounts (AWS Academy / Vocareum / sandbox labs) SES is denied -
# we detect that and quietly fall back to Cognito's built-in email.

def sender_status():
    """SES verification status for SENDER_EMAIL, or None if SES can't be used."""
    try:
        resp = ses.get_identity_verification_attributes(Identities=[SENDER_EMAIL])
    except ClientError as e:
        print(f'  SES unavailable ({e.response["Error"]["Code"]}).')
        print('  -> Falling back to Cognito built-in email. Codes are sent from')
        print('     no-reply@verificationemail.com (check your spam folder).')
        return None
    attr = resp.get('VerificationAttributes', {}).get(SENDER_EMAIL, {})
    return attr.get('VerificationStatus')


def configure_pool_email(pool_id):
    """Send codes via SES when possible; otherwise keep Cognito's built-in email."""
    status = sender_status()
    if status is None:
        return  # SES not usable in this account - keep default email

    if status != 'Success':
        try:
            ses.verify_email_identity(EmailAddress=SENDER_EMAIL)
            print(f'  SES sender not verified yet: {SENDER_EMAIL}')
            print(f'  -> AWS just emailed {SENDER_EMAIL} a verification link.')
            print('  -> Click it, then redeploy to send codes via SES.')
        except ClientError as e:
            print(f'  Could not start SES verification ({e.response["Error"]["Code"]}).')
        print('  Using Cognito built-in email until SES is verified.')
        return

    try:
        account_id = boto3.client('sts', region_name=REGION).get_caller_identity()['Account']
        cognito.update_user_pool(
            UserPoolId=pool_id,
            AutoVerifiedAttributes=['email'],
            Policies={'PasswordPolicy': PASSWORD_POLICY},
            AccountRecoverySetting=ACCOUNT_RECOVERY,
            EmailConfiguration={
                'EmailSendingAccount': 'DEVELOPER',
                'SourceArn': f'arn:aws:ses:{REGION}:{account_id}:identity/{SENDER_EMAIL}',
                'From': f'SeatMe <{SENDER_EMAIL}>',
            },
            VerificationMessageTemplate={
                'DefaultEmailOption': 'CONFIRM_WITH_CODE',
                'EmailSubject': 'Your SeatMe verification code',
                'EmailMessage': 'Welcome to SeatMe! Your verification code is {####}',
            },
        )
        print(f'  Cognito now sends verification emails via SES as {SENDER_EMAIL}')
    except ClientError as e:
        print(f'  Could not attach SES ({e.response["Error"]["Code"]}); using built-in email.')


# ─── Permission groups + demo accounts ─────────────────────────────────────

def ensure_group(pool_id, name, description, precedence):
    """Create a Cognito group if it does not already exist."""
    try:
        cognito.create_group(
            GroupName=name, UserPoolId=pool_id,
            Description=description, Precedence=precedence,
        )
        print(f'  Created group: {name}')
    except cognito.exceptions.GroupExistsException:
        print(f'  Group already exists: {name}')


def ensure_user(pool_id, email, password, group=None):
    """Create a confirmed user with a known permanent password (idempotent)."""
    try:
        cognito.admin_create_user(
            UserPoolId=pool_id,
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'},
            ],
            MessageAction='SUPPRESS',   # do not email the demo accounts
        )
        print(f'  Created user: {email}')
    except cognito.exceptions.UsernameExistsException:
        print(f'  User already exists: {email}')
    cognito.admin_set_user_password(
        UserPoolId=pool_id, Username=email, Password=password, Permanent=True,
    )
    if group:
        cognito.admin_add_user_to_group(
            UserPoolId=pool_id, Username=email, GroupName=group,
        )


def seed_users(pool_id):
    """Create the demo admin + host accounts. Best-effort: restricted lab
    accounts may deny these admin APIs, so we warn and continue."""
    try:
        ensure_group(pool_id, ADMIN_GROUP, 'Platform administrators - manage all events', 1)
        ensure_group(pool_id, HOST_GROUP, 'Event hosts - manage their own event', 10)
        ensure_user(pool_id, ADMIN_EMAIL, ADMIN_PASSWORD, group=ADMIN_GROUP)
        ensure_user(pool_id, DEMO_HOST_EMAIL, DEMO_HOST_PASSWORD, group=HOST_GROUP)
        print(f'  Demo admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}')
        print(f'  Demo host:  {DEMO_HOST_EMAIL} / {DEMO_HOST_PASSWORD}')
    except ClientError as e:
        print(f'  Could not seed demo users ({e.response["Error"]["Code"]}); create them manually.')


def configure_post_confirmation_trigger(pool_id):
    """Attach the auth_post_confirmation Lambda as the pool's Post-Confirmation
    trigger so every newly confirmed sign-up is auto-added to the 'host' group.

    Best-effort: the trigger function is deployed by setup_aws.py. If it is not
    present yet (e.g. setup_cognito.py run on its own) we warn and continue -
    sign-up still works, users just won't be auto-grouped until a full deploy.
    """
    try:
        account_id = boto3.client('sts', region_name=REGION).get_caller_identity()['Account']
        fn_arn = f'arn:aws:lambda:{REGION}:{account_id}:function:{TRIGGER_FN_NAME}'
        pool_arn = f'arn:aws:cognito-idp:{REGION}:{account_id}:userpool/{pool_id}'
        lambda_client = boto3.client('lambda', region_name=REGION)

        # The function must exist before Cognito will accept it as a trigger.
        lambda_client.get_function(FunctionName=TRIGGER_FN_NAME)

        # 1) Allow Cognito to invoke the trigger.
        try:
            lambda_client.add_permission(
                FunctionName=TRIGGER_FN_NAME,
                StatementId=f'cognito-{pool_id}',
                Action='lambda:InvokeFunction',
                Principal='cognito-idp.amazonaws.com',
                SourceArn=pool_arn,
            )
        except lambda_client.exceptions.ResourceConflictException:
            pass  # permission already granted

        # 2) Point the pool's PostConfirmation trigger at the function while
        #    preserving the rest of the pool configuration.
        pool = cognito.describe_user_pool(UserPoolId=pool_id)['UserPool']
        lambda_config = pool.get('LambdaConfig', {})
        lambda_config['PostConfirmation'] = fn_arn
        kwargs = {
            'UserPoolId': pool_id,
            'Policies': pool.get('Policies', {'PasswordPolicy': PASSWORD_POLICY}),
            'AutoVerifiedAttributes': pool.get('AutoVerifiedAttributes', ['email']),
            'AccountRecoverySetting': pool.get('AccountRecoverySetting', ACCOUNT_RECOVERY),
            'LambdaConfig': lambda_config,
        }
        email_cfg = pool.get('EmailConfiguration') or {}
        if email_cfg.get('EmailSendingAccount') == 'DEVELOPER':
            kwargs['EmailConfiguration'] = email_cfg
            vmt = pool.get('VerificationMessageTemplate')
            if vmt:
                kwargs['VerificationMessageTemplate'] = vmt
        cognito.update_user_pool(**kwargs)
        print(f"  Post-confirmation trigger attached: new sign-ups -> '{HOST_GROUP}' group")
    except ClientError as e:
        code = e.response['Error']['Code']
        print(f'  Could not attach post-confirmation trigger ({code}).')
        print(f'  Ensure the backend is deployed (setup_aws.py creates {TRIGGER_FN_NAME}), then redeploy.')


def setup_cognito():
    """Create the user pool + app client, wire up email, seed the admin/host
    groups and demo accounts, attach the post-confirmation trigger, then return
    (pool_id, client_id)."""
    pool_id = create_user_pool()
    client_id = create_app_client(pool_id)
    configure_pool_email(pool_id)
    seed_users(pool_id)
    configure_post_confirmation_trigger(pool_id)
    return pool_id, client_id


def delete_user_pool():
    """Delete the SeatMe user pool (and its app clients) if it exists."""
    pool_id = find_pool_id()
    if not pool_id:
        print('    User pool does not exist - skipping')
        return
    cognito.delete_user_pool(UserPoolId=pool_id)
    print(f'    Deleted user pool {pool_id}')


if __name__ == '__main__':
    pid, cid = setup_cognito()
    print(f'\nUSER_POOL_ID = {pid}')
    print(f'CLIENT_ID    = {cid}')
