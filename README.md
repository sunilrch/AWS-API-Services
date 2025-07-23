#  AWS VPC Management API


##  Objective

Create a secure, serverless API using AWS services that:

- Creates a **VPC with multiple subnets** via a POST request.
- Stores the resulting resource data in **DynamoDB**.
- Allows authenticated users to **retrieve** created VPCs via GET requests.
- Uses **IAM-based authentication** (not Cognito).
- Is written in **Python** and deployed via AWS Lambda + API Gateway.

---

## Architecture Overview


This project uses the following AWS services:

- **API Gateway** – REST API interface.
- **Lambda (Python)** – Business logic for creating and retrieving VPCs.
- **EC2 (boto3)** – Used to create VPCs and subnets.
- **DynamoDB** – Stores created VPC metadata (VPC ID, subnets, CIDR block).
- **IAM** – Secures the API using AWS IAM authentication.

---

##  Project Structure


.vpc-api-iam
├── src/
│ ├── create_vpc.py # Lambda function for creating VPC and subnets
│ ├── get_vpc.py # Lambda function for getting a single VPC by ID
├── template.yaml # SAM/CloudFormation template 
├── requirements.txt
└── README.md

** Please not that the samconfig.toml will get auto created once you deploy the template using SAM CLI
** The sam template template.yaml will provision all the necessary serverless services on aws

---

##  Deployment Steps


### Install Dependencies

1. Install AWS CLI

2. Install SAM CLI (Serverless application model)

3. Install python version 3.13 on your system.

4. Install boto3 package 

   pip install boto3


5. Deploy Lambdas ( via SAM template)

cd vpc-api-iam

sam build
sam deploy --guided


---

##  Authentication


This API uses IAM-based authentication:

All API Gateway methods require AWS Signature V4 (SigV4) signed requests.

Only authenticated IAM users or roles can access the endpoints.

Authorization is open to all authenticated users, no fine-grained roles.

You can test using AWS CLI with:

aws apigateway test-invoke-method --rest-api-id <api-id> --resource-id <resource-id> --http-method POST --path-with-query-string "/vpcs" --body "{\"cidr_block\": \"10.0.0.0/16\", \"subnet_count\": 3}"

---

## API Endpoints

POST /vpcs

Creates a new VPC with subnets.

Payload:

{
  "cidr_block": "10.0.0.0/16",
  "subnet_count": 3
}

Response:
{
  "vpc_id": "vpc-*****",
  "cidr_block": "10.0.0.0/16",
  "subnets": ["subnet-abc", "subnet-def", "subnet-ghi"]
}

 GET /vpcs

Returns a list of all created VPCs.

[
  {
    "vpc_id": "vpc-*****",
    "cidr_block": "10.0.0.0/16",
    "subnets": ["subnet-abc", "subnet-def"]
  }
]

---


## DynamoDB Schema

Your table should have the following:

Primary Key: vpc_id (string)

Attributes:

    cidr_block (string)

    subnets (list)

---


## Testing

You can test the endpoints using using an IAM user account have necessary permissions to invoke API gateway:


AWS CLI

aws apigateway test-invoke-method --rest-api-id <api-gw-id> --resource-id <resource-id> --http-method POST --path-with-query-string "/vpcs" --body "{\"cidr_block\": \"10.0.0.0/16\", \"subnet_count\": 3}"

aws apigateway test-invoke-method --rest-api-id <api-gw-id>--resource-id <resource-id> --http-method GET --path-with-query-string "/vpcs" 

API Gateway Console (Test Invoke)
