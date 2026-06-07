"""
SeatMe Frontend Deployment to S3
====================================
Uploads all frontend files to S3 as a static website.
Also injects the API Gateway URL into every HTML/JS file automatically.

Usage:
  python3 deploy_frontend.py --api-url https://XXXX.execute-api.us-east-1.amazonaws.com

The public website URL is printed at the end.
"""

import os
import json
import argparse
import mimetypes
import subprocess
import boto3
from botocore.exceptions import ClientError

REGION = 'us-east-1'

sts = boto3.client('sts', region_name=REGION)

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = SCRIPT_DIR

# ─── Bucket name (unique per account) ─────────────────────────────────────

def get_bucket_name():
    account_id = sts.get_caller_identity()['Account']
    return f'seatme-{account_id}'

# ─── Create Bucket ─────────────────────────────────────────────────────────

def create_bucket(bucket_name):
    # Use AWS CLI – handles regional endpoint quirks automatically
    try:
        result = subprocess.run(
            ['aws', 's3api', 'create-bucket', '--bucket', bucket_name, '--region', REGION],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f'  Created bucket: {bucket_name}')
        elif 'BucketAlreadyOwnedByYou' in result.stderr or 'already exists' in result.stderr.lower():
            print(f'  Bucket already exists: {bucket_name}')
        else:
            raise RuntimeError(result.stderr.strip())
    except FileNotFoundError:
        # AWS CLI not found – fall back to boto3
        s3 = boto3.client('s3', region_name=REGION)
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f'  Created bucket: {bucket_name}')
        except ClientError as e:
            code = e.response['Error']['Code']
            if code in ('BucketAlreadyOwnedByYou', 'BucketAlreadyExists'):
                print(f'  Bucket already exists: {bucket_name}')
            else:
                raise

def set_public_access(bucket_name):
    # Use AWS CLI for reliability
    account_id = sts.get_caller_identity()['Account']
    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }]
    })
    website_config = json.dumps({
        "IndexDocument": {"Suffix": "index.html"},
        "ErrorDocument": {"Key": "index.html"}
    })

    cmds = [
        ['aws', 's3api', 'delete-public-access-block', '--bucket', bucket_name],
        ['aws', 's3api', 'put-bucket-policy',  '--bucket', bucket_name, '--policy', policy],
        ['aws', 's3api', 'put-bucket-website', '--bucket', bucket_name,
         '--website-configuration', website_config],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f'  Warning: {" ".join(cmd[2:3])} – {result.stderr.strip()}')

    print('  Public access and static website hosting enabled')

# ─── Inject deploy-time config ─────────────────────────────────────────────

def inject_config(content: bytes, api_url: str,
                  user_pool_id: str = None, client_id: str = None) -> bytes:
    """Replaces the API URL and Cognito placeholders in HTML/JS files."""
    text = content.decode('utf-8', errors='replace')
    text = text.replace('https://REPLACE_WITH_YOUR_API_URL', api_url)
    if user_pool_id:
        text = text.replace('REPLACE_WITH_COGNITO_USER_POOL_ID', user_pool_id)
    if client_id:
        text = text.replace('REPLACE_WITH_COGNITO_CLIENT_ID', client_id)
    return text.encode('utf-8')

# ─── Upload Files ──────────────────────────────────────────────────────────

def upload_files(bucket_name: str, api_url: str,
                 user_pool_id: str = None, client_id: str = None):
    s3 = boto3.client('s3', region_name=REGION)
    print(f'\n  Uploading files from: {FRONTEND_DIR}')
    uploaded = 0

    for fname in os.listdir(FRONTEND_DIR):
        fpath = os.path.join(FRONTEND_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        # Skip Python scripts
        if fname.endswith('.py'):
            continue

        with open(fpath, 'rb') as f:
            content = f.read()

        ext = os.path.splitext(fname)[1].lower()
        if ext in ('.html', '.htm', '.js'):
            content = inject_config(content, api_url, user_pool_id, client_id)

        mime, _ = mimetypes.guess_type(fname)
        mime = mime or 'application/octet-stream'

        s3.put_object(Bucket=bucket_name, Key=fname, Body=content, ContentType=mime)
        print(f'  Uploaded: {fname}')
        uploaded += 1

    print(f'\n  Total files uploaded: {uploaded}')

# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--api-url',
        required=True,
        help='The API Base URL printed by setup_aws.py'
    )
    parser.add_argument('--user-pool-id', help='Cognito User Pool ID (from setup_cognito.py)')
    parser.add_argument('--client-id', help='Cognito App Client ID (from setup_cognito.py)')
    args = parser.parse_args()
    api_url = args.api_url.rstrip('/')

    bucket_name = get_bucket_name()

    print('=== SeatMe Frontend Deploy ===\n')
    print(f'API URL:     {api_url}')
    print(f'Bucket name: {bucket_name}')

    print('\n── Creating S3 Bucket ──')
    create_bucket(bucket_name)
    set_public_access(bucket_name)

    print('\n── Uploading Files ──')
    upload_files(bucket_name, api_url, args.user_pool_id, args.client_id)

    website_url = f'http://{bucket_name}.s3-website-{REGION}.amazonaws.com'
    print('\n' + '='*50)
    print('Frontend deployed successfully!')
    print(f'\nWebsite URL:\n  {website_url}')
    print('='*50)

if __name__ == '__main__':
    main()
