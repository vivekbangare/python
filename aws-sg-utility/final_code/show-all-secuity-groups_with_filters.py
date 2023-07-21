import boto3
import logging

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

# Configure the logging settings
logging.basicConfig(filename='aws_security_group_analysis.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Get a list of all AWS regions
ec2_client = session.client('ec2')
regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

# Desired FromPort values to filter
desired_ports = [22, 3389, 8080, 80, 9090, 443]

# Function to process security groups and print information for each region
def process_security_groups(session, region_name):
    try:

        # Create an EC2 client using the session
        ec2_client = session.client('ec2', region_name=region_name)

        # Describe security groups
        response = ec2_client.describe_security_groups()

         # print(f"\nProcessing Security Groups in Region: {region_name}")
        for group in response['SecurityGroups']:
            # Filter the IpPermissions based on desired FromPort values
            filtered_permissions = [
                permission for permission in group['IpPermissions']
                if 'FromPort' in permission and permission['FromPort'] in desired_ports
                #and len(permission.get('IpRanges', [])) == 1
                and any(ip_range['CidrIp'] == '0.0.0.0/0' for ip_range in permission.get('IpRanges', []))
            ]

            # If the group has at least one matching permission, print its information
            if filtered_permissions:
                print('Region:', region_name)
                print('Security Group ID:', group['GroupId'])
                print('Security Group Name:', group['GroupName'])
                print('VPC ID:', group['VpcId'])
                logging.info('Region: %s', region_name)
                logging.info('Security Group ID: %s', group['GroupId'])
                logging.info('Security Group Name: %s', group['GroupName'])
                logging.info('VPC ID: %s', group['VpcId'])

                # Display the IpPermissions for the filtered ports
                print('Inbound Rules:')
                logging.info('Inbound Rules:')
                for permission in filtered_permissions:
                    from_port = permission.get('FromPort', 'N/A')
                    to_port = permission.get('ToPort', 'N/A')
                    ip_ranges = permission.get('IpRanges', [])

                    print(f'\tFrom Port: {from_port}, To Port: {to_port}, CidrIPs: {[ip["CidrIp"] for ip in ip_ranges]}')
                    logging.info('\tFrom Port: %s, To Port: %s, CidrIPs: %s', from_port, to_port,[ip["CidrIp"] for ip in ip_ranges])

                print('-' * 50)
                logging.info('-' * 50)

    except Exception as e:
        logging.error('Error processing security groups in region %s: %s', region_name, str(e))       

# Iterate over all the desired regions
for region_name in regions:
    process_security_groups(session, region_name)
