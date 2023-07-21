import boto3
from tqdm import tqdm
from tabulate import tabulate


# Replace these with your AWS credentials if needed
aws_access_key_id = ''
aws_secret_access_key = ''
default_region = 'us-east-1'

# Output file name
output_file = 'security_group_analysis_output.txt'

# Function to retrieve AWS account name and ID
def get_aws_account_info(access_key_id, secret_access_key):
    try:
        # Create an IAM client using the provided access key and secret key
        iam_client = boto3.client('iam', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

        # Get the AWS account alias (name)
        response = iam_client.list_account_aliases()
        if 'AccountAliases' in response and len(response['AccountAliases']) > 0:
            account_name = response['AccountAliases'][0]
        else:
            account_name = 'N/A'  # Account alias not set

        # Get the AWS account ID
        account_id = iam_client.get_user()["User"]["Arn"].split(":")[4]

        return account_name, account_id
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None

# Get AWS account info
account_name, account_id = get_aws_account_info(aws_access_key_id, aws_secret_access_key)

# Create a session using your credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=default_region
)

# Get a list of all AWS regions
ec2_client = session.client('ec2')
regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
total_region_count = len(regions)

# Function to process security groups and return counts
def process_security_groups(session, region_name):
    # Create a session using your credentials and the current region
  #  session = boto3.Session(
  #      aws_access_key_id=aws_access_key_id,
  #      aws_secret_access_key=aws_secret_access_key,
  #      region_name=region_name
  #  )

    # Create an EC2 client using the session
    ec2_client = session.client('ec2',region_name=region_name)

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
        desired_ports = [22, 80, 8080, 3389, 9090, 443]
        filtered_permissions = [
            permission for permission in group['IpPermissions']
            if 'FromPort' in permission and permission['FromPort'] in desired_ports
        ]

        # If the group has at least one matching permission, increment counts
        if filtered_permissions:
            desired_ports_count += 1

            # Check if the group has all desired ports open to 0.0.0.0/0
            if all('list is empty' if not permission.get('IpRanges') else permission['IpRanges'][0].get('CidrIp') == '0.0.0.0/0' for permission in filtered_permissions):
                desired_ports_open_to_all_count += 1

    return total_count, desired_ports_count, desired_ports_open_to_all_count

# Initialize counts for all regions
total_count_all_regions = 0
desired_ports_count_all_regions = 0
desired_ports_open_to_all_count_all_regions = 0

# Define the progress bar
progress_bar = tqdm(regions, desc="Processing Regions", unit="Region", dynamic_ncols=True, leave=False)

# List to store region-specific data
region_data_list = []

# Iterate over all the desired regions with tqdm progress bar
for region_name in progress_bar:
    total_count, desired_ports_count, desired_ports_open_to_all_count = process_security_groups(session, region_name)
    total_count_all_regions += total_count
    desired_ports_count_all_regions += desired_ports_count
    desired_ports_open_to_all_count_all_regions += desired_ports_open_to_all_count

    # Append the region-specific data to the list
    region_data_list.append([region_name, total_count, desired_ports_count, desired_ports_open_to_all_count])

    # Move the cursor to the beginning of the line and clear the line
    print('\r', end='')

# Print the region-specific data
print(tabulate(region_data_list, headers=["Region", "Total Security Groups", "Desired Ports (22, 80, 8080, 3389)", "0.0.0.0/0 open with Desired Ports"], tablefmt="grid"))

# Print the AWS account info and total counts for all regions
print("AWS Account Name:", account_name)
print("AWS Account ID:", account_id)
print("Total Region count:", total_region_count)
print("Total Security Groups in All Regions:", total_count_all_regions)
print("Total Security Groups with Desired Ports in All Regions:", desired_ports_count_all_regions)
print("Total Security Groups with Desired Ports open to 0.0.0.0/0 in All Regions:", desired_ports_open_to_all_count_all_regions)

# Write the data to the output file
with open(output_file, 'w') as file:
    file.write(tabulate(region_data_list, headers=["Region", "Total Security Groups", "Desired Ports (22, 80, 8080, 3389)", "0.0.0.0/0 open with Desired Ports"], tablefmt="grid"))
    file.write("\n\n")
    file.write("AWS Account Name: " + account_name + "\n")
    file.write("AWS Account ID: " + account_id + "\n")
    file.write("Total Region count: " + str(total_region_count) + "\n")
    file.write("Total Security Groups in All Regions: " + str(total_count_all_regions) + "\n")
    file.write("Total Security Groups with Desired Ports in All Regions: " + str(desired_ports_count_all_regions) + "\n")
    file.write("Total Security Groups with Desired Ports open to 0.0.0.0/0 in All Regions: " + str(desired_ports_open_to_all_count_all_regions) + "\n")
