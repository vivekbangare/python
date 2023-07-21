import boto3
from tqdm import tqdm

# Replace these with your AWS credentials if needed
aws_access_key_id = ''
aws_secret_access_key = ''
default_region= 'us-east-1'

# Create a session using your credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=default_region
)

# Get a list of all AWS regions
ec2_client = session.client('ec2')
regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

# Function to process security groups and return counts
def process_security_groups(session, region_name):
    # Create a session using your credentials and the current region
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=default_region
    )

    # Create an EC2 client using the session
    ec2_client = session.client('ec2', region_name=region_name)

    # Describe security groups
    response = ec2_client.describe_security_groups()

    # Initialize counts
    total_count = 0
    desired_ports_count = 0
    desired_ports_open_to_all_count = 0

    # Process the security groups for the filtered ports
    for group in response['SecurityGroups']:
        total_count += 1

        # Filter the IpPermissions based on desired FromPort values
        desired_ports = [22, 80, 8080, 3389]
        filtered_permissions = [
            permission for permission in group['IpPermissions']
            if 'FromPort' in permission and permission['FromPort'] in desired_ports
        ]

        # If the group has at least one matching permission, increment counts
        if filtered_permissions:
            desired_ports_count += 1

            # Check if the group has all desired ports open to 0.0.0.0/0
            if all('list is empty' if not permission.get('IpRanges') else permission['IpRanges'][0].get('CidrIp') == '0.0.0.0/0' for permission in filtered_permissions):
            #if all(permission.get('IpRanges') and permission['IpRanges'][0].get('CidrIp') == '0.0.0.0/0' for permission in filtered_permissions):
                desired_ports_open_to_all_count += 1

    return total_count, desired_ports_count, desired_ports_open_to_all_count

# Initialize counts for all regions
total_count_all_regions = 0
desired_ports_count_all_regions = 0
desired_ports_open_to_all_count_all_regions = 0

# Define the progress bar
progress_bar = tqdm(regions, desc="Processing", unit="Region", dynamic_ncols=True, leave=False)

# Iterate over all the desired regions
for region_name in progress_bar:
    total_count, desired_ports_count, desired_ports_open_to_all_count = process_security_groups(session, region_name)
    total_count_all_regions += total_count
    desired_ports_count_all_regions += desired_ports_count
    desired_ports_open_to_all_count_all_regions += desired_ports_open_to_all_count

 #   print(f"Region: {region_name}")
 #   print(f"Total Security Groups: {total_count}")
 #   print(f"Desired Ports (22, 80, 8080, 3389): {desired_ports_count}")
 #   print(f"0.0.0.0/0 open with Desired Ports : {desired_ports_open_to_all_count}")
 #   print('-' * 50)

print()

print("Total Security Groups in All Regions:", total_count_all_regions)
print("Total Security Groups with Desired Ports in All Regions:", desired_ports_count_all_regions)
print("Total Security Groups with Desired Ports open to 0.0.0.0/0 in All Regions:", desired_ports_open_to_all_count_all_regions)
