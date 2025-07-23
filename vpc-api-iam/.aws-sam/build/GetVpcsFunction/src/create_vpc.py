# src/create_vpc.py
import json
import boto3
import uuid
import os

ec2 = boto3.client('ec2')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DDB_TABLE'])

def lambda_handler(event, context):
    body = json.loads(event['body'])
    cidr_block = body.get('cidr_block', '10.0.0.0/16')
    subnet_count = body.get('subnet_count', 2)

    # Create VPC
    vpc = ec2.create_vpc(CidrBlock=cidr_block)
    vpc_id = vpc['Vpc']['VpcId']

    subnets = []
    for i in range(subnet_count):
        subnet_cidr = f"10.0.{i}.0/24"
        subnet = ec2.create_subnet(VpcId=vpc_id, CidrBlock=subnet_cidr)
        subnets.append(subnet['Subnet']['SubnetId'])

    # Store in DynamoDB
    item = {
        "vpc_id": vpc_id,
        "subnets": subnets,
        "cidr_block": cidr_block
    }
    table.put_item(Item=item)

    return {
        'statusCode': 201,
        'body': json.dumps(item)
    }
