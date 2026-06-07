"""
SeatMe – Full AWS Setup Script
================================
Runs all setup steps automatically:
  1. Finds the correct IAM role in the account
  2. Deploys all Lambda functions
  3. Creates an HTTP API Gateway
  4. Links each route to the matching Lambda function
  5. Prints the API_BASE_URL

Run from CloudShell:
  cd SeatMe/backend/deploy
  python3 setup_aws.py
"""

import os
import io
import time
import zipfile
import boto3

REGION = 'us-east-1'
RUNTIME = 'python3.12'
API_NAME = 'SeatMe-API'

# Lambda name → (method, route)
ROUTES = [
    ('add_host',          'POST',   '/hosts'),
    ('get_host',          'GET',    '/hosts'),
    ('update_host',       'PUT',    '/hosts'),
    ('delete_host',       'DELETE', '/hosts'),
    ('add_guest',         'POST',   '/guests'),
    ('get_guests',        'GET',    '/guests'),
    ('update_guest',      'PUT',    '/guests'),
    ('delete_guest',      'DELETE', '/guests'),
    ('rsvp_guest',        'POST',   '/guests/rsvp'),
    ('generate_seating',  'POST',   '/seating'),
    ('set_tables',        'POST',   '/tables'),
    ('send_invitation',  'POST',   '/invitations/send'),
    ('list_hosts',        'GET',    '/admin/hosts'),
]

# Lambda functions that are NOT HTTP routes (e.g. Cognito triggers). They are
# deployed like the others but get no API Gateway integration/route.
TRIGGER_FUNCTIONS = ['auth_post_confirmation']

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
# Lambda handler sources live in ../lambdas (this script is in backend/deploy)
LAMBDAS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'lambdas'))

sts      = boto3.client('sts',            region_name=REGION)
iam      = boto3.client('iam',            region_name=REGION)
lmb      = boto3.client('lambda',         region_name=REGION)
apigw    = boto3.client('apigatewayv2',   region_name=REGION)

# ─── helpers ───────────────────────────────────────────────────────────────

def get_account_id():
    return sts.get_caller_identity()['Account']

def find_role_arn(account_id):
    """
    Tries LabRole first. If not found, automatically selects the first
    role that has a Lambda trust policy.
    """
    try:
        iam.get_role(RoleName='LabRole')
        print('  Found LabRole')
        return f'arn:aws:iam::{account_id}:role/LabRole'
    except iam.exceptions.NoSuchEntityException:
        pass

    # Search for any role with Lambda trust
    paginator = iam.get_paginator('list_roles')
    for page in paginator.paginate():
        for role in page['Roles']:
            doc = role['AssumeRolePolicyDocument']
            statements = doc.get('Statement', [])
            for s in statements:
                principal = s.get('Principal', {})
                service = principal.get('Service', '')
                if isinstance(service, str):
                    service = [service]
                if 'lambda.amazonaws.com' in service:
                    print(f'  Found suitable role: {role["RoleName"]}')
                    return role['Arn']

    raise RuntimeError(
        'No Lambda-compatible role found. '
        'Make sure a role with lambda.amazonaws.com trust policy exists.'
    )

def zip_lambda(name):
    py_file = os.path.join(LAMBDAS_DIR, f'{name}.py')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.write(py_file, f'{name}.py')
        # Bundle shared helpers (auth) so handlers can `import _common`.
        common = os.path.join(LAMBDAS_DIR, '_common.py')
        if os.path.exists(common):
            zf.write(common, '_common.py')
    return buf.getvalue()

# ─── Step 1: Deploy Lambdas ────────────────────────────────────────────────

def deploy_lambdas(role_arn):
    print('\n── Step 1: Deploying Lambda functions ──')
    failed = []
    for name in [n for n, _, _ in ROUTES] + TRIGGER_FUNCTIONS:
        fn_name = f'SeatMe-{name}'
        code    = zip_lambda(name)
        try:
            lmb.create_function(
                FunctionName=fn_name,
                Runtime=RUNTIME,
                Role=role_arn,
                Handler=f'{name}.lambda_handler',
                Code={'ZipFile': code},
                Timeout=30,
                MemorySize=128,
            )
            print(f'  Created  {fn_name}')
        except lmb.exceptions.ResourceConflictException:
            lmb.update_function_code(FunctionName=fn_name, ZipFile=code)
            # Keep configuration in sync on redeploys (handler/timeout/role/runtime).
            try:
                lmb.get_waiter('function_updated').wait(FunctionName=fn_name)
                lmb.update_function_configuration(
                    FunctionName=fn_name,
                    Runtime=RUNTIME,
                    Role=role_arn,
                    Handler=f'{name}.lambda_handler',
                    Timeout=30,
                    MemorySize=128,
                )
            except Exception as e:
                print(f'  (config update skipped for {fn_name}: {e})')
            print(f'  Updated  {fn_name}')
        except Exception as e:
            print(f'  FAILED   {fn_name}: {e}')
            failed.append(name)

    if failed:
        raise RuntimeError(f'Lambda deployment failed: {", ".join(failed)}')
    print('  All functions deployed successfully')

# ─── Step 2: API Gateway ───────────────────────────────────────────────────

def get_lambda_arn(name, account_id):
    return (
        f'arn:aws:lambda:{REGION}:{account_id}'
        f':function:SeatMe-{name}'
    )

def allow_apigw_invoke(fn_name, api_id, account_id):
    """Grants API Gateway permission to invoke the Lambda function."""
    statement_id = f'apigw-{api_id}-{fn_name}'
    try:
        lmb.add_permission(
            FunctionName=fn_name,
            StatementId=statement_id,
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:{REGION}:{account_id}:{api_id}/*/*',
        )
    except lmb.exceptions.ResourceConflictException:
        pass  # Permission already exists

def setup_api_gateway(account_id):
    print('\n── Step 2: Setting up API Gateway ──')

    # Reuse existing API if already created
    existing = apigw.get_apis()['Items']
    api = next((a for a in existing if a['Name'] == API_NAME), None)

    if api:
        api_id = api['ApiId']
        print(f'  Existing API found: {api_id}')
    else:
        api = apigw.create_api(
            Name=API_NAME,
            ProtocolType='HTTP',
            CorsConfiguration={
                'AllowOrigins': ['*'],
                'AllowMethods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                'AllowHeaders': ['Content-Type', 'Authorization'],
            },
        )
        api_id = api['ApiId']
        print(f'  Created API: {api_id}')

    # Wait for Lambda functions to become active
    print('  Waiting for functions to become active...')
    time.sleep(5)

    existing_routes = {
        r['RouteKey']: r['RouteId']
        for r in apigw.get_routes(ApiId=api_id)['Items']
    }
    existing_integrations = apigw.get_integrations(ApiId=api_id)['Items']

    for name, method, path in ROUTES:
        fn_name    = f'SeatMe-{name}'
        route_key  = f'{method} {path}'
        lambda_arn = get_lambda_arn(name, account_id)
        uri        = (
            f'arn:aws:apigateway:{REGION}:lambda:path'
            f'/2015-03-31/functions/{lambda_arn}/invocations'
        )

        # Create integration if it doesn't exist
        existing_int = next(
            (i for i in existing_integrations
             if i.get('IntegrationUri') == uri),
            None
        )
        if existing_int:
            integration_id = existing_int['IntegrationId']
        else:
            integ = apigw.create_integration(
                ApiId=api_id,
                IntegrationType='AWS_PROXY',
                IntegrationUri=uri,
                PayloadFormatVersion='2.0',
            )
            integration_id = integ['IntegrationId']

        # Create route if it doesn't exist
        if route_key not in existing_routes:
            apigw.create_route(
                ApiId=api_id,
                RouteKey=route_key,
                Target=f'integrations/{integration_id}',
            )
            print(f'  Created route: {route_key} -> {fn_name}')
        else:
            print(f'  Route exists: {route_key}')

        allow_apigw_invoke(fn_name, api_id, account_id)

    # Create default stage with auto-deploy
    stages = apigw.get_stages(ApiId=api_id)['Items']
    if not any(s['StageName'] == '$default' for s in stages):
        apigw.create_stage(
            ApiId=api_id,
            StageName='$default',
            AutoDeploy=True,
        )
        print('  Created $default stage')

    endpoint = f'https://{api_id}.execute-api.{REGION}.amazonaws.com'
    return endpoint

# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    print('=== SeatMe AWS Setup ===\n')
    account_id = get_account_id()
    print(f'Account: {account_id}')

    print('\n── Finding IAM Role ──')
    role_arn = find_role_arn(account_id)
    print(f'  Role: {role_arn}')

    deploy_lambdas(role_arn)
    endpoint = setup_api_gateway(account_id)

    print('\n' + '='*50)
    print('All done!')
    print(f'\nAPI_BASE_URL = "{endpoint}"')
    print('\nCopy this URL and run:')
    print(f'  python3 deploy_frontend.py --api-url {endpoint}')
    print('='*50)

if __name__ == '__main__':
    main()
