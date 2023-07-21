import boto3

# Replace these with your AWS credentials if needed
aws_access_key_id = ''
aws_secret_access_key = ''
default_region = 'us-east-1'

# Create a session using your credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=default_region
)

# Get a list of all AWS regions
ec2_client = session.client('ec2')
regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

# Desired FromPort values to filter
desired_ports = [22, 9090, 443, 8080, 80, 3389]

# Function to process security groups and delete inbound rules for each region
def process_security_groups(session, region_name):
    # Create an EC2 client using the session
    ec2_client = session.client('ec2', region_name=region_name)

    # Describe security groups
    response = ec2_client.describe_security_groups()

    print(f"\nProcessing Security Groups in Region: {region_name}")

    # Process and delete the inbound rules for '0.0.0.0/0' from the filtered security groups
    for group in response['SecurityGroups']:
        # Filter the IpPermissions based on desired FromPort values and open-to-all CidrIp (0.0.0.0/0)
        for permission in group['IpPermissions']:
            if 'FromPort' in permission and permission['FromPort'] in desired_ports:
                for ip_range in permission.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        matching_port = permission['FromPort']
                        print(f'Deleting Inbound Rule for Security Group ID in {region_name} (Port {matching_port}):', group['GroupId'])
                        try:
                            ec2_client.revoke_security_group_ingress(
                                GroupId=group['GroupId'],
                                IpPermissions=[
                                    {
                                        'IpProtocol': permission.get('IpProtocol', '-1'),
                                        'FromPort': permission.get('FromPort', -1),
                                        'ToPort': permission.get('ToPort', -1),
                                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                                    },
                                ]
                            )
                            print(f'Inbound Rule {matching_port} Deleted Successfully.')
                        except Exception as e:
                            print(f'Error deleting Inbound Rule: {str(e)}')
                        break  

# Iterate over all the desired regions
for region_name in regions:
    process_security_groups(session, region_name)
