import boto3

def main():
    # Initialize the AWS session using the default profile
    session = boto3.Session(profile_name='master')

    # Create an S3 client using the default session
    s3_client = session.client('s3')

    try:
        # List all S3 buckets
        response = s3_client.list_buckets()

        # Print the bucket names
        print("S3 Buckets:")
        for bucket in response['Buckets']:
            print(bucket['Name'])

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
