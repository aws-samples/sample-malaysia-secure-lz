import boto3
import os
from typing import Optional
import logging
from botocore.exceptions import ClientError
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_delegated_admin(service: str, region_name: str, delegated_admin_account_id: str) -> Optional[dict]:
    """
    Set delegated admin for a given AWS service.

    :param service: The AWS service name (e.g., 'guardduty', 'securityhub')
    :param region_name: The AWS region name
    :param delegated_admin_account_id: The AWS account ID of the delegated admin
    :return: The response from the API call, or None if an error occurred
    """
    client = boto3.client(service, region_name=region_name)
    try:
        response = client.enable_organization_admin_account(
            AdminAccountId=delegated_admin_account_id
        )
        logger.info(f"Successfully set {service} delegated admin to {delegated_admin_account_id}")
        return response
    except ClientError as e:
        logger.error(f"Error setting {service} delegated admin: {e}")
        return None

def set_guardduty_protection_plan(region_name: str, delegated_admin_account_id: str) -> Optional[dict]:
    """
    Set GuardDuty protection plan.

    :param region_name: The AWS region name
    :param protection_plan_name: The name of the protection plan
    :return: The response from the API call, or None if an error occurred
    """
    client = boto3.client('guardduty', region_name=region_name)
    try:
        response = client.create_detector(
            Enable=True,
            Features=[
                {
                    'Name': 'S3_DATA_EVENTS',
                    'Status': 'ENABLED'
                },
                {
                    'Name': 'EKS_AUDIT_LOGS',
                    'Status': 'ENABLED'
                },
                {
                    'Name': 'EBS_MALWARE_PROTECTION',
                    'Status': 'ENABLED'
                },
                {
                    'Name': 'RDS_LOGIN_EVENTS',
                    'Status': 'ENABLED'
                },
                {
                    'Name': 'LAMBDA_NETWORK_LOGS',
                    'Status': 'ENABLED'
                },
                {
                    'Name': 'RUNTIME_MONITORING',
                    'Status': 'ENABLED',
                    'AdditionalConfiguration': [
                        {
                            'Name': 'EC2_AGENT_MANAGEMENT',
                            'Status': 'ENABLED'
                        }
                    ]
                }
            ]            
        )
        logger.info(f"Successfully set GuardDuty protection plan")
        return response
    except ClientError as e:
        logger.error(f"Error setting GuardDuty protection plan: {e}")
        return None

def validate_account_id(account_id):
    if not account_id or not account_id.isdigit() or len(account_id) != 12:
        raise ValueError("Invalid AWS account ID")

def validate_region_name(region_name):
    # This is a simple check. In a production environment, you might want to check against a list of valid AWS regions.
    if not region_name or not isinstance(region_name, str):
        raise ValueError("Invalid AWS region name")

def main():
    try:
        account_id = os.environ.get('AWS_ACCOUNT_ID')
        region_name = os.environ.get('AWS_REGION')
        homeregion_name = os.environ.get('HOME_REGION')
        # get common line arguments
        parser = argparse.ArgumentParser("security-config")
        parser.add_argument("delegated_admin_account", help="security delegated admin account", type=str)
        args = parser.parse_args()
        delegated_admin_account_id = args.delegated_admin_account
        
        if not account_id:
            logger.error("Please set the AWS_ACCOUNT_ID environment variable")
            return
        if not region_name:
            logger.error("Please set the AWS_REGION environment variable")
            return
        if not delegated_admin_account_id:
            logger.error("Please specify the delegated_admin_account command line argument")
            return

        validate_account_id(account_id)
        validate_account_id(delegated_admin_account_id)
        validate_region_name(region_name)
        validate_region_name(homeregion_name)

        # Set delegated admins for various services        
        # delegated admin for GuardDuty
        client_guardduty = boto3.client("guardduty", region_name=homeregion_name)
        try:
            response = client_guardduty.enable_organization_admin_account(AdminAccountId=delegated_admin_account_id)
            logger.info(f"Successfully set GuardDuty delegated admin to {delegated_admin_account_id}")
            # Set GuardDuty protection plan
            set_guardduty_protection_plan(region_name, delegated_admin_account_id)
        except client_guardduty.exceptions.BadRequestException as e:
            logger.info(f"GuardDuty delegated admin is already set to {delegated_admin_account_id}, {e}")
        except ClientError as e:
            logger.error(f"Error setting GuardDuty delegated admin: {e}")
            return
        

        # delegated admin for Security Hub
        client_securityhub = boto3.client("securityhub", region_name=homeregion_name)
        try:
            response = client_securityhub.enable_organization_admin_account(AdminAccountId=delegated_admin_account_id)
            logger.info(f"Successfully set Security Hub delegated admin to {delegated_admin_account_id}")
        except client_securityhub.exceptions.ResourceConflictException as e:
            logger.info(f"Security Hub delegated admin is already set to {delegated_admin_account_id}, {e}")
        except ClientError as e:
            logger.error(f"Error setting Security Hub delegated admin: {e}")
            return
        
        # delegated admin for Inspector2 (not yet supported in Malaysia region)
        # client_inspector2 = boto3.client("inspector2", region_name=homeregion_name)
        # try:
        #     response = client_inspector2.enable_delegated_admin_account(delegatedAdminAccountId=delegated_admin_account_id)
        #     logger.info(f"Successfully set Inspector2 delegated admin to {delegated_admin_account_id}")
        # except client_inspector2.exceptions.ConflictException as e:
        #     logger.info(f"Inspector2 delegated admin is already set to {delegated_admin_account_id}, {e}")
        # except ClientError as e:
        #     logger.error(f"Error setting Inspector2 delegated admin: {e}")
        #     return
        
        # delegated admin for Firewall Manager (not yet supported in Malaysia region)
        # client_fms = boto3.client("fms", region_name="us-east-1")
        # try:
        #     response = client_fms.associate_admin_account(AdminAccount=delegated_admin_account_id)
        #     logger.info(f"Successfully set Firewall Manager delegated admin to {delegated_admin_account_id}")
        # except ClientError as e:
        #     logger.error(f"Error setting Firewall Manager delegated admin: {e}")
        #     return
        
        # delegated admin for Detective (not yet supported in Malaysia region)
        # client_detective = boto3.client("detective", region_name=homeregion_name)
        # try:
        #     response = client_detective.enable_organization_admin_account(AccountId=delegated_admin_account_id)
        #     logger.info(f"Successfully set Detective delegated admin to {delegated_admin_account_id}")
        # except client_detective.exceptions.ConflictException as e:
        #     logger.info(f"Detective delegated admin is already set to {delegated_admin_account_id}, {e}")
        # except ClientError as e:
        #     logger.error(f"Error setting Detective delegated admin: {e}")
        #     return
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        # Implement rollback logic here if needed
if __name__ == "__main__":
    main()
