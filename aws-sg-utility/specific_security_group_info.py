import boto3

aws_access_key_id = ''
aws_secret_access_key = ''
region_name = 'us-west-2'
security_group_id = 'sg-'  

# Create a session using your credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

# Create an EC2 client using the session
ec2_client = session.client('ec2')

# Describe the specific security group by providing its ID in a list
response = ec2_client.describe_security_groups(GroupIds=[security_group_id])

# Process and print the security group information
for group in response['SecurityGroups']:
    print('Security Group ID:', group['GroupId'])
    print('Security Group Name:', group['GroupName'])
    print('VPC ID:', group['VpcId'])

    # Display the IpPermissions
    print('Inbound Rules:')
    for permission in group['IpPermissions']:
        from_port = permission.get('FromPort', 'N/A')
        to_port = permission.get('ToPort', 'N/A')
        ip_ranges = permission.get('IpRanges', [])
        
        print(f'\tFrom Port: {from_port}, To Port: {to_port}, CidrIPs: {[ip["CidrIp"] for ip in ip_ranges]}')
    
    print('-' * 50)
