import boto3
import os

def read_config_file(config_file_path):
    with open(config_file_path, 'r') as file:
        config_data = file.readlines()
    
    aws_access_key_id = config_data[0].strip()
    aws_secret_access_key = config_data[1].strip()
    desired_regions = config_data[2].strip().split(',')
    desired_ports = [int(port.strip()) for port in config_data[3].strip().split(',')]
    
    return aws_access_key_id, aws_secret_access_key, desired_regions, desired_ports

def delete_security_groups():
    current_directory = os.getcwd()
    config_file_path = os.path.join(current_directory, 'config.ini')
    aws_access_key_id, aws_secret_access_key, _, _ = read_config_file(config_file_path)

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    with open("generated_security_groups.txt", "r") as file:
        for line in file:
            group_id, region = line.strip().split(',')
            ec2_client = session.client('ec2', region_name=region)

            try:
                ec2_client.delete_security_group(GroupId=group_id)
                print(f"Security Group '{group_id}' in region '{region}' deleted successfully.")
            except Exception as e:
                print(f"Error deleting security group {group_id} in region {region}: {str(e)}")

if __name__ == "__main__":
    delete_security_groups()
