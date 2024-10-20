import boto3
import os

# Sets up default security guardrails for the account by region
# 1. Set alternate contact information (Security, Billing, Operations)
# 2. Delete default VPC
# 3. Enable EBS default encryption
# 4. Enable EC2 IMDSv2 as mandatory
# 5. Enable Block Public Access to S3, AMI, EBS Snapshots at account level


def update_alternate_contact(account_id, contact_type, email, name, phone, title):
    """
    Update an AWS account's alternate contact information.

    :param account_id: The 12-digit AWS account ID
    :param contact_type: The type of alternate contact (BILLING, OPERATIONS, or SECURITY)
    :param email: Email address of the alternate contact
    :param name: Name of the alternate contact
    :param phone: Phone number of the alternate contact
    :param title: Title of the alternate contact
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('account')

    try:
        # Call the put_alternate_contact method
        response = account_client.put_alternate_contact(
            AccountId=account_id,
            AlternateContactType=contact_type,
            EmailAddress=email,
            Name=name,
            PhoneNumber=phone,
            Title=title
        )
        print(f"Successfully updated {contact_type} alternate contact for account {account_id}")
        return response
    except Exception as e:
        print(f"Error updating alternate contact: {str(e)}")
        return None



#write function to delete default vpc
def delete_default_vpc(account_id):
    """
    Delete the default VPC in an AWS account.

    :param account_id: The 12-digit AWS account ID
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('ec2', region_name=region_name)

    try:
        # Call the delete_default_vpc method
        response = account_client.delete_vpc(
            AccountId=account_id
        )
        print(f"Successfully deleted default VPC for account {account_id}")
        return response
    except Exception as e:
        print(f"Error deleting default VPC: {str(e)}")
        return None
    

#write function to set ebs default encryption
def enable_ebs_default_encryption(account_id, region_name):
    """
    Set EBS default encryption for an AWS account.

    :param account_id: The 12-digit AWS account ID
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('ec2', region_name=region_name)

    try:
        # Call the set_ebs_default_encryption method
        response = account_client.enable_ebs_encryption_by_default(
            DryRun=False
        )
        print(f"Successfully set EBS default encryption for account {account_id}")
        return response
    except Exception as e:
        print(f"Error setting EBS default encryption: {str(e)}")
        return None

#write function to enable block public access for AMIs
def enable_block_public_access_for_amis(account_id, region_name):
    """
    Enable block public access for AMIs in an AWS account.

    :param account_id: The 12-digit AWS account ID
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('ec2', region_name=region_name)

    try:
        # Call the enable_block_public_access_for_amis method
        response = account_client.enable_image_block_public_access(
            ImageBlockPublicAccessState='block-new-sharing',
            DryRun=False
        )
        print(f"Successfully enabled block public access for AMIs for account {account_id}")
        return response
    except Exception as e:
        print(f"Error enabling block public access for AMIs: {str(e)}")
        return None

#write function to enable block public access for EBS snapshots
def enable_block_public_access_for_snapshots(account_id, region_name):
    """
    Enable block public access for EBS Snapshots in an AWS account.

    :param account_id: The 12-digit AWS account ID
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('ec2', region_name=region_name)

    try:
        # Call the enable_snapshot_block_public_access method
        response = account_client.enable_snapshot_block_public_access(
            State='block-all-sharing',
            DryRun=False
        )
        print(f"Successfully enabled block public access for EBS snapshots for account {account_id}")
        return response
    except Exception as e:
        print(f"Error enabling block public access for AMIs: {str(e)}")
        return None

#write function to enable S3 block public access
def enable_s3_block_public_access(account_id, region_name):
    """
    Set S3 block public access for an AWS account.

    :param account_id: The 12-digit AWS account ID
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('s3control', region_name=region_name)

    try:
        # Call the set_s3_block_public_access method
        response = account_client.put_public_access_block(
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            },
            AccountId=account_id
        )
        print(f"Successfully set S3 block public access for account {account_id}")
        return response
    except Exception as e:
        print(f"Error setting S3 block public access: {str(e)}")
        return None

#write function to enable EC2 instance metadata
def enable_ec2_instance_metadata(account_id, region_name):
    """
    Enable EC2 instance metadata for an AWS account.

    :param account_id: The 12-digit AWS account ID
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('ec2', region_name=region_name)

    try:
        # Call the enable_ec2_instance_metadata method
        response = account_client.modify_instance_metadata_defaults(
            HttpTokens='required',
            HttpPutResponseHopLimit=1,
            HttpEndpoint='enabled',
            InstanceMetadataTags='disabled',
            DryRun=False
        )
        print(f"Successfully enabled EC2 instance metadata for account {account_id}")
        return response
    except Exception as e:
        print(f"Error enabling EC2 instance metadata: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    # Fetch account ID from environment variable for security
    account_id = os.environ.get('AWS_ACCOUNT_ID')
    region_name = os.environ.get('AWS_REGION')
    homeregion_name = os.environ.get('HOME_REGION')

    if not account_id:
        print("Please set the AWS_ACCOUNT_ID environment variable")
    elif not region_name:
        print("Please set the REGION_NAME environment variable")
    elif not homeregion_name:
        print("Please set the HOME_REGION environment variable")
    else:
        enable_ebs_default_encryption(account_id, homeregion_name)
        enable_s3_block_public_access(account_id, homeregion_name)
        enable_block_public_access_for_amis(account_id, homeregion_name)
        enable_block_public_access_for_snapshots(account_id, homeregion_name)
        enable_ec2_instance_metadata(account_id, homeregion_name)
        # update_alternate_contact(
        #     account_id=account_id,
        #     contact_type='BILLING',
        #     email='billing@example.com',
        #     name='John Doe',
        #     phone='+1234567890',
        #     title='Finance Manager'
        # )