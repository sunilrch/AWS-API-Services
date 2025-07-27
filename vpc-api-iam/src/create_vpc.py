import json
import boto3
import os
import logging
import ipaddress  # For dynamic subnet calculation

# Initialize boto3 clients
ec2 = boto3.client('ec2')
dynamodb = boto3.resource('dynamodb')

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get DynamoDB table name from environment variable
table_name = os.environ['DDB_TABLE']
table = dynamodb.Table(table_name)

def create_vpc(cidr_block):
    """Create a VPC with the provided CIDR block."""
    try:
        logger.info(f"Creating VPC with CIDR: {cidr_block}")
        vpc = ec2.create_vpc(CidrBlock=cidr_block)
        vpc_id = vpc['Vpc']['VpcId']
        logger.info(f"VPC created successfully with ID: {vpc_id}")
        return vpc_id
    except Exception as e:
        logger.error(f"Error creating VPC: {str(e)}")
        raise

def create_subnet(vpc_id, subnet_cidr):
    """Create a subnet inside the VPC."""
    try:
        logger.info(f"Creating subnet with CIDR: {subnet_cidr} in VPC: {vpc_id}")
        subnet = ec2.create_subnet(VpcId=vpc_id, CidrBlock=subnet_cidr)
        subnet_id = subnet['Subnet']['SubnetId']
        logger.info(f"Subnet created successfully with ID: {subnet_id}")
        return subnet_id
    except Exception as e:
        logger.error(f"Error creating subnet: {str(e)}")
        raise

def store_vpc_info(vpc_id, subnets, cidr_block):
    """Store the VPC and subnet information in DynamoDB."""
    try:
        region = ec2.meta.region_name
        logger.info(f"Storing VPC information for VPC ID: {vpc_id} in DynamoDB.")
        item = {
            "vpc_id": vpc_id,
            "subnets": subnets,
            "cidr_block": cidr_block,
            "region": region
        }
        table.put_item(Item=item)
        logger.info("VPC information stored successfully.")
    except Exception as e:
        logger.error(f"Error storing VPC information in DynamoDB: {str(e)}")
        raise

def lambda_handler(event, context):
    """Main Lambda handler function."""
    try:
        # Parse the incoming event body
        body = json.loads(event['body'])

        # ✅ Validate cidr_block is present
        cidr_block = body.get('cidr_block')
        if not cidr_block:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'cidr_block is required'})
            }

        # Optional: Validate subnet_count or use default
        subnet_count = int(body.get('subnet_count', 2))
        if subnet_count < 1:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'subnet_count must be >= 1'})
            }

        # Step 1: Create VPC
        vpc_id = create_vpc(cidr_block)

        # Step 2: Generate subnets from CIDR
        network = ipaddress.ip_network(cidr_block)
        subnet_blocks = list(network.subnets(new_prefix=24))

        if subnet_count > len(subnet_blocks):
            raise ValueError(f"CIDR block {cidr_block} cannot accommodate {subnet_count} /24 subnets.")

        subnets = []
        for i in range(subnet_count):
            subnet_cidr = str(subnet_blocks[i])
            subnet_id = create_subnet(vpc_id, subnet_cidr)
            subnets.append(subnet_id)

        # Step 3: Store in DynamoDB
        store_vpc_info(vpc_id, subnets, cidr_block)

        # Return success response
        return {
            'statusCode': 201,
            'body': json.dumps({
                'vpc_id': vpc_id,
                'subnets': subnets,
                'cidr_block': cidr_block
            })
        }

    except Exception as e:
        logger.error(f"Error in Lambda function: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
