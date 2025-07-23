# src/get_vpcs.py
import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DDB_TABLE'])

def lambda_handler(event, context):
    result = table.scan()
    return {
        'statusCode': 200,
        'body': json.dumps(result['Items'])
    }
