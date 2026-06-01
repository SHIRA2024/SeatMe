"""
SeatMe Project
Lambda Deployment Script

Deploys all Lambda functions using boto3.
Creates new functions or updates existing ones automatically.

Run from the lambdas folder in AWS CloudShell:
  python3 deploy_lambdas.py

AWS credentials are provided automatically by CloudShell.
"""

import os
import io
import zipfile
import boto3

REGION = 'us-east-1'
RUNTIME = 'python3.12'

LAMBDAS = [
    'add_host',
    'delete_host',
    'get_host',
    'update_host',
    'add_guest',
    'delete_guest',
    'get_guests',
    'update_guest',
    'rsvp_guest',
    'generate_seating',
    'set_tables',
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sts_client = boto3.client('sts', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)


def get_role_arn():
    account_id = sts_client.get_caller_identity()['Account']
    return f'arn:aws:iam::{account_id}:role/LabRole'


def read_code(lambda_name):
    py_file = os.path.join(SCRIPT_DIR, f'{lambda_name}.py')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.write(py_file, f'{lambda_name}.py')
    return buf.getvalue()


def deploy_lambda(lambda_name, role_arn):
    function_name = f'SeatMe-{lambda_name}'
    code = read_code(lambda_name)

    try:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime=RUNTIME,
            Role=role_arn,
            Handler=f'{lambda_name}.lambda_handler',
            Code={'ZipFile': code},
            Timeout=10,
            MemorySize=128,
        )
        print(f'  Created {function_name}')
        return True
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=code,
        )
        print(f'  Updated {function_name}')
        return True
    except Exception as e:
        print(f'  FAILED {function_name}: {e}')
        return False


def main():
    role_arn = get_role_arn()
    print(f'Using role: {role_arn}\n')

    failed = []
    for name in LAMBDAS:
        print(f'Deploying {name}...')
        ok = deploy_lambda(name, role_arn)
        if not ok:
            failed.append(name)

    print()
    if failed:
        print(f'Failed: {", ".join(failed)}')
    else:
        print('All Lambda functions deployed successfully!')


if __name__ == '__main__':
    main()
