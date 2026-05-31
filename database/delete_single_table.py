"""
SeatMe Project
Delete Single Table Script
"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('SeatMe')

table.delete()

print("SeatMe table deleted successfully!")