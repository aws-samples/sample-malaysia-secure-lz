import boto3
import os
import json
import logging
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sets up AWS Organizations
# 1. Setup required OUs
#   - name: Security
#  - name: Infrastructure
#  - name: Sandbox
#  - name: Forensic
#  - name: Workloads
#  - name: Suspended

def validate_account_id(account_id):
    if not account_id or not account_id.isdigit() or len(account_id) != 12:
        raise ValueError("Invalid AWS account ID")

def validate_region_name(region_name):
    # This is a simple check. In a production environment, you might want to check against a list of valid AWS regions.
    if not region_name or not isinstance(region_name, str):
        raise ValueError("Invalid AWS region name")

#write funcntion to create organization unit
def create_organization_unit(account_id, name, parent_id):
    """
    Create an AWS Organizations unit.

    :param account_id: The 12-digit AWS account ID
    :param region_name: The AWS region name
    :param name: The name of the unit
    :param parent_id: The ID of the parent unit
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('organizations', region_name='us-east-1')

    try:
        # Call the create_organization_unit method
        response = account_client.create_organizational_unit(
            Name=name,
            ParentId=parent_id,
            Tags = [
                {
                    'Key': 'CreatedBy',
                    'Value': 'accelerator'
                }
            ]
        )
        logger.info(f"Successfully created organization unit {name} for account {account_id}")
        return response
    except ClientError as e:
        logger.error(f"Error creating organization unit: {str(e)}")
        raise

#write function to create service control policy
def create_service_control_policy(account_id, name, description, content):
    """
    Create an AWS Organizations service control policy.

    :param account_id: The 12-digit AWS account ID
    :param region_name: The AWS region name
    :param name: The name of the policy
    :param description: The description of the policy
    :param content: The content of the policy
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('organizations')
    try:
        # Call the create_service_control_policy method
        response = account_client.create_policy(
            Content=content,
            Description=description,
            Name=name,
            Type='SERVICE_CONTROL_POLICY'
        )
        logger.info(f"Successfully created service control policy {name} for account {account_id}")
        return response
    except ClientError as e:
        logger.error(f"Error creating service control policy: {str(e)}")
        raise

#write function to attach service control policy to organization unit
def attach_service_control_policy(account_id, policy_id, ou_id):
    """
    Attach an AWS Organizations service control policy to an organization unit.

    :param account_id: The 12-digit AWS account ID
    :param region_name: The AWS region name
    :param policy_id: The ID of the policy
    :param ou_id: The ID of the organization unit
    """
    # Create a boto3 client for the account service
    account_client = boto3.client('organizations')
    try:
        # Call the attach_policy method
        response = account_client.attach_policy(
            PolicyId=policy_id,
            TargetId=ou_id
        )
        logger.info(f"Successfully attached service control policy {policy_id} to organization unit {ou_id} for account {account_id}")
        return response
    except ClientError as e:
        logger.error(f"Error attaching service control policy: {str(e)}")
        raise

def load_policy_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.loads(file.read())
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error loading policy content from {file_path}: {e}")
        raise

# Start the creation of Organization related controls
if __name__ == "__main__":
    try:
        account_id = os.environ.get('AWS_ACCOUNT_ID')
        region_name = os.environ.get('AWS_REGION')
        homeregion_name = os.environ.get('HOME_REGION')

        validate_account_id(account_id)
        validate_region_name(region_name)
        validate_region_name(homeregion_name)

        client = boto3.client('organizations', region_name='us-east-1')
        organization_roots = client.list_roots()
        if not organization_roots:
            raise ValueError("No organization roots found")

        organization_rootid = organization_roots['Roots'][0]['Id']

        # Create OUs
        ous = {
            'Security': create_organization_unit(account_id, 'Security', organization_rootid),
            'Infrastructure': create_organization_unit(account_id, 'Infrastructure', organization_rootid),
            'Sandbox': create_organization_unit(account_id, 'Sandbox', organization_rootid),
            'Forensic': create_organization_unit(account_id, 'Forensic', organization_rootid),
            'Workloads': create_organization_unit(account_id, 'Workloads', organization_rootid),
            'Suspended': create_organization_unit(account_id, 'Suspended', organization_rootid)
        }

        # Create and attach policies
        policies = {
            'lza-guardrails': load_policy_content('service-control-policies/my-lza-guardrails.json'),
            'lza-data-guardrails': load_policy_content('service-control-policies/my-lza-data-guardrails.json')
        }

        for policy_name, policy_content in policies.items():
            policy = create_service_control_policy(account_id, policy_name, f'Malaysia LZA default {policy_name}', json.dumps(policy_content))
            policy_id = policy['Policy']['PolicySummary']['Id']

            for ou_name in ['Security', 'Infrastructure', 'Workloads']:
                attach_service_control_policy(account_id, policy_id, ous[ou_name]['OrganizationalUnit']['Id'])

        logger.info("Script completed successfully")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        # Implement rollback logic here if needed
