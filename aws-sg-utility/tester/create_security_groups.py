import boto3
import random
import string
import os

def read_config_file(config_file_path):
    with open(config_file_path, 'r') as file:
        config_data = file.readlines()
    
    aws_access_key_id = config_data[0].strip()
    aws_secret_access_key = config_data[1].strip()
    desired_regions = config_data[2].strip().split(',')
    desired_ports = [int(port.strip()) for port in config_data[3].strip().split(',')]
    
    return aws_access_key_id, aws_secret_access_key, desired_regions, desired_ports
# Function to generate a random security group name
def generate_random_name(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# Function to create a security group with the desired inbound rules
def create_security_group_with_rules(ec2_client, group_name, vpc_id, desired_ports):
    try:
        response = ec2_client.create_security_group(
            GroupName=group_name,
            Description='Security Group with Random Name',
            VpcId=vpc_id
        )
        group_id = response['GroupId']
        
        for port in desired_ports:
            ec2_client.authorize_security_group_ingress(
                GroupId=group_id,
                IpProtocol='tcp',
                FromPort=port,
                ToPort=port,
                CidrIp='0.0.0.0/0'
            )
        
        print(f"Security Group '{group_name}' (ID: {group_id}) created with inbound rules for ports {desired_ports}.")
        return group_id
    except Exception as e:
        print(f"Error creating security group: {str(e)}")
        return None

def get_first_vpc_id(ec2_client):
    response = ec2_client.describe_vpcs()
    if 'Vpcs' in response:
        return response['Vpcs'][0]['VpcId']
    return None

def main():
    current_directory = os.getcwd()
    config_file_path = os.path.join(current_directory, 'config.ini')
    aws_access_key_id, aws_secret_access_key, desired_regions, desired_ports = read_config_file(config_file_path)

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    security_groups_info = []  # List to store security group IDs and regions

    for region_name in desired_regions:
        ec2_client = session.client('ec2', region_name=region_name)

        random_group_name = generate_random_name()
        vpc_id = get_first_vpc_id(ec2_client)

        if vpc_id:
            group_id = create_security_group_with_rules(ec2_client, random_group_name, vpc_id, desired_ports)
            if group_id is not None: # Check if the group_id is not None before adding to the list
                security_groups_info.append((group_id, region_name))

    # Write the security group IDs and regions to a file
    with open("generated_security_groups.txt", "w") as file:
        for group_id, region in security_groups_info:
            file.write(f"{group_id},{region}\n")

if __name__ == "__main__":
    main()
