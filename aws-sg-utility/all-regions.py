import boto3

# Replace these with your AWS credentials if needed
aws_access_key_id = ''
aws_secret_access_key = ''

# Create a session using your credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# Get a list of all AWS regions
ec2_client = session.client('ec2')
regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

# Print the list of regions
print("Available AWS Regions:")
for region in regions:
    print(region)
