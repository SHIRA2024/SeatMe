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

# ─── Inject API URL ────────────────────────────────────────────────────────

def inject_api_url(content: bytes, api_url: str, filename: str) -> bytes:
    text = content.decode('utf-8', errors='replace')
    text = text.replace('https://REPLACE_WITH_YOUR_API_URL', api_url)

    if filename.lower().endswith(('.html', '.htm')) and '_api.js' not in filename:
        api_config = f'\n<script>window.SEATME_API_BASE = "{api_url}";</script>\n'
        api_script = '<script src="_api.js"></script>\n'
        if '</head>' in text:
            text = text.replace('</head>', api_config + '</head>', 1)
        if '</body>' in text and '<script src="_api.js">' not in text:
            text = text.replace('</body>', api_script + '</body>', 1)

    return text.encode('utf-8')

# ─── Upload Files ──────────────────────────────────────────────────────────

def upload_files(bucket_name: str, api_url: str):
    s3 = boto3.client('s3', region_name=REGION)
    print(f'\n  Uploading files from: {FRONTEND_DIR}')
    uploaded = 0

    # Upload all files, then copy login screen as index.html
    login_file = 'SCD540~1.HTM'

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
            content = inject_api_url(content, api_url, fname)

        mime, _ = mimetypes.guess_type(fname)
        mime = mime or 'application/octet-stream'

        s3.put_object(Bucket=bucket_name, Key=fname, Body=content, ContentType=mime)
        print(f'  Uploaded: {fname}')
        uploaded += 1

    # Set login screen as the homepage
    if login_file in os.listdir(FRONTEND_DIR):
        s3.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': login_file},
            Key='index.html',
            MetadataDirective='COPY'
        )
        print(f'  Set {login_file} as index.html')

    print(f'\n  Total files uploaded: {uploaded}')

# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--api-url',
        required=True,
        help='The API Base URL printed by setup_aws.py'
    )
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
    upload_files(bucket_name, api_url)

    website_url = f'http://{bucket_name}.s3-website-{REGION}.amazonaws.com'
    print('\n' + '='*50)
    print('Frontend deployed successfully!')
    print(f'\nWebsite URL:\n  {website_url}')
    print('='*50)

if __name__ == '__main__':
    main()
