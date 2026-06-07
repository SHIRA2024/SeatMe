#!/usr/bin/env python3
"""
SeatMe - Deploy (with optional clean)
=====================================
Deploys the whole SeatMe stack. By default it ONLY deploys; pass --clean to
delete all existing resources first.

  Teardown order:  S3 bucket  ->  API Gateway  ->  Lambda functions  ->  DynamoDB table
  Deploy order:    DynamoDB table  ->  Lambda functions + API Gateway  ->  Frontend (S3)

This script reuses the existing helpers so there is a single source of truth:
  - backend/deploy/setup_aws.py      (Lambda functions + API Gateway)
  - backend/deploy/setup_cognito.py  (Cognito user pool + app client)
  - backend/deploy/seed_example.py   (example data: host + 50 guests)
  - frontend/deploy_frontend.py      (Frontend upload to S3)

Run from AWS CloudShell at the repository root:

  python3 redeploy_all.py            # deploy the stack (no teardown)
  python3 redeploy_all.py --seed     # deploy + insert example data (host + 50 guests)
  python3 redeploy_all.py --clean    # delete everything first, then deploy
  python3 redeploy_all.py --teardown # only remove resources (no deploy)
  python3 redeploy_all.py --yes      # skip the confirmation prompt (with --clean/--teardown)

AWS credentials are provided automatically by CloudShell.
"""

import os
import sys
import runpy
import argparse

import boto3
from botocore.exceptions import ClientError

REGION = 'us-east-1'
TABLE_NAME = 'SeatMe'

ROOT = os.path.dirname(os.path.abspath(__file__))
DEPLOY_DIR = os.path.join(ROOT, 'backend', 'deploy')
FRONTEND_DIR = os.path.join(ROOT, 'frontend')

# Make the existing deployment scripts importable so we reuse their logic.
sys.path.insert(0, DEPLOY_DIR)
sys.path.insert(0, FRONTEND_DIR)

import setup_aws        # noqa: E402  - deploys Lambda functions + API Gateway
import setup_cognito    # noqa: E402  - creates the Cognito user pool + app client
import deploy_frontend  # noqa: E402  - deploys the frontend to S3

# boto3 clients used for teardown
sts = boto3.client('sts', region_name=REGION)
dynamodb = boto3.client('dynamodb', region_name=REGION)
lmb = boto3.client('lambda', region_name=REGION)
apigw = boto3.client('apigatewayv2', region_name=REGION)
s3 = boto3.resource('s3', region_name=REGION)


# ─── helpers ───────────────────────────────────────────────────────────────

def banner(text):
    print('\n' + '=' * 60)
    print(f'  {text}')
    print('=' * 60)


# ─── Teardown ──────────────────────────────────────────────────────────────

def delete_frontend_bucket():
    bucket_name = deploy_frontend.get_bucket_name()
    print(f'  S3 bucket: {bucket_name}')
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.objects.all().delete()
        bucket.delete()
        print('    Deleted bucket and all objects')
    except ClientError as e:
        code = e.response['Error']['Code']
        if code in ('NoSuchBucket', '404', 'NoSuchKey'):
            print('    Bucket does not exist - skipping')
        else:
            print(f'    Warning: {e}')


def delete_api_gateway():
    print(f'  API Gateway: {setup_aws.API_NAME}')
    apis = apigw.get_apis().get('Items', [])
    found = False
    for api in apis:
        if api['Name'] == setup_aws.API_NAME:
            apigw.delete_api(ApiId=api['ApiId'])
            print(f'    Deleted API {api["ApiId"]}')
            found = True
    if not found:
        print('    API does not exist - skipping')


def delete_lambdas():
    print('  Lambda functions:')
    names = [name for name, _, _ in setup_aws.ROUTES] + getattr(setup_aws, 'TRIGGER_FUNCTIONS', [])
    for name in names:
        fn_name = f'SeatMe-{name}'
        try:
            lmb.delete_function(FunctionName=fn_name)
            print(f'    Deleted {fn_name}')
        except lmb.exceptions.ResourceNotFoundException:
            print(f'    {fn_name} not found - skipping')


def delete_table():
    print(f'  DynamoDB table: {TABLE_NAME}')
    try:
        dynamodb.delete_table(TableName=TABLE_NAME)
        print('    Delete requested, waiting for removal...')
        dynamodb.get_waiter('table_not_exists').wait(TableName=TABLE_NAME)
        print('    Table deleted')
    except dynamodb.exceptions.ResourceNotFoundException:
        print('    Table does not exist - skipping')


def delete_cognito():
    print('  Cognito user pool:')
    setup_cognito.delete_user_pool()


def teardown():
    banner('TEARDOWN - removing all SeatMe resources')
    delete_frontend_bucket()
    delete_api_gateway()
    delete_lambdas()
    delete_table()
    delete_cognito()


# ─── Deploy ────────────────────────────────────────────────────────────────

def create_table():
    print(f'  Creating DynamoDB table: {TABLE_NAME}')
    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST',
        )
        print('    Waiting for table to become active...')
        dynamodb.get_waiter('table_exists').wait(TableName=TABLE_NAME)
        print('    Table is active')
    except dynamodb.exceptions.ResourceInUseException:
        print('    Table already exists - skipping')


def seed_data():
    # seed_example.py seeds data by invoking the deployed Lambda functions,
    # so it must run only after the Lambdas exist. It returns the example host
    # email (via its module globals) so we can print a shareable preview link.
    print('  Seeding example data (host + 50 guests via seed_example)...')
    ns = runpy.run_path(os.path.join(DEPLOY_DIR, 'seed_example.py'), run_name='__main__')
    return ns.get('HOST_EMAIL')


def deploy(account_id, do_seed):
    banner('DEPLOY - DynamoDB table')
    create_table()

    banner('DEPLOY - Lambda functions + API Gateway')
    role_arn = setup_aws.find_role_arn(account_id)
    print(f'  Role: {role_arn}')
    setup_aws.deploy_lambdas(role_arn)
    endpoint = setup_aws.setup_api_gateway(account_id)
    print(f'\n  API_BASE_URL = {endpoint}')

    demo_host = None
    if do_seed:
        banner('DEPLOY - Seed example data (seed_example)')
        demo_host = seed_data()

    banner('DEPLOY - Cognito user pool')
    user_pool_id, client_id = setup_cognito.setup_cognito()
    print(f'  User pool:  {user_pool_id}')
    print(f'  App client: {client_id}')

    banner('DEPLOY - Frontend (S3)')
    bucket_name = deploy_frontend.get_bucket_name()
    deploy_frontend.create_bucket(bucket_name)
    deploy_frontend.set_public_access(bucket_name)
    deploy_frontend.upload_files(bucket_name, endpoint, user_pool_id, client_id)
    website_url = f'http://{bucket_name}.s3-website-{REGION}.amazonaws.com'

    return endpoint, website_url, demo_host


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Deploy the SeatMe stack. By default it only deploys; use --clean to delete everything first.'
    )
    parser.add_argument('--yes', action='store_true', help='Skip the confirmation prompt')
    parser.add_argument('--seed', action='store_true', help='Insert example data (host + 50 guests) after deploying the Lambdas')
    parser.add_argument('--clean', action='store_true', help='Delete all existing resources before deploying')
    parser.add_argument('--teardown', action='store_true', help='Only remove resources (no deploy)')
    args = parser.parse_args()

    if args.teardown:
        do_teardown = True
        do_deploy = False
    else:
        do_teardown = args.clean
        do_deploy = True

    account_id = sts.get_caller_identity()['Account']

    print('=== SeatMe Auto Redeploy ===')
    print(f'Account: {account_id}')
    print(f'Region:  {REGION}')
    steps = ('teardown ' if do_teardown else '') + ('deploy' if do_deploy else '')
    print(f'Steps:   {steps.strip()}')

    if do_teardown and not args.yes:
        print('\n  WARNING: this DELETES the SeatMe table (all data), Lambda functions,')
        print('  the API Gateway, the Cognito user pool (all host accounts) and the')
        print('  S3 website bucket.')
        if input('  Type "yes" to continue: ').strip().lower() != 'yes':
            print('Aborted.')
            return

    if do_teardown:
        teardown()

    endpoint = website_url = demo_host = None
    if do_deploy:
        endpoint, website_url, demo_host = deploy(account_id, args.seed)

    banner('DONE')
    if endpoint:
        print(f'  API URL:     {endpoint}')
    if website_url:
        print(f'  Website URL: {website_url}')
        if demo_host:
            print(f'  Demo host:   {website_url}/host.html?host={demo_host}')
            print('               ^ opens the example dashboard with no login required')
        print('\n  Open the Website URL to use SeatMe.')


if __name__ == '__main__':
    main()
