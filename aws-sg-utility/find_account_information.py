import boto3

def get_aws_account_id(access_key_id, secret_access_key):
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

# Replace these with your AWS credentials if needed
aws_access_key_id = ''
aws_secret_access_key = ''

account_name, account_id = get_aws_account_id(aws_access_key_id, aws_secret_access_key)

if account_name and account_id:
    print(f"AWS Account Name: {account_name}")
    print(f"AWS Account ID: {account_id}")
else:
    print("Failed to retrieve AWS account information.")
