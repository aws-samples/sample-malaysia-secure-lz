# Malaysia LZA (Beta)

This beta release of the landing zone accelerator (LZA) is for Malaysia public sector agencies and partners to deploy "Secure by Default" guardrails for their AWS multi-account landing zone. CGSO cloud requirements are transposed into configurable infrastrcuture as code (IaC) scripts. 

## Prerequisites:
Complete these validation checks before starting the deployment of the LZA. 
1. AWS management account has been created. 
2. AWS environment does not have any running workloads and services. 
3. All deny Service Control Policies (SCPs) are detached from OUs.
4. Validate which of these OU Organization structure (Infrastructure, Security, Workloads, Sandbox, Suspended) are created. If these are in place, comment these out from "organization-config.py".
5. Prepare separate emails for log-archive and audit accounts that will be created when Control Tower is initiated.
6. Disable existing AWS security services (Security Hub, Config, GuardDuty, Detective, Inspector) across all the regions. Remove delegated administration setting for each of the services. 
7. Enable opt-in Malaysia (ap-southeast-5) region from AWS Organization console.
8. Check for suspended accounts in the Organization. These would not be enrolled to Control Tower, and will be isolated under Suspended OU.

## Deployment Steps
1. Identify the AWS Organization identifer (format o-XXXXXX) from the AWS Organization console of the management account. This is an input parameter to the script.
2. Identify the OU identifer (format ou-XXXXXX) of the Infrastructure OU. Capture the OU to share the new Transit-Gateway resource. 
aws organizations describe-organizational-unit --organizational-unit-id <OU_ID> --query 'OrganizationalUnit.Arn'
3. Create KMS Customer Managed Key (Symmetric, for Encrypt and Decrypt), KMS-CMK, for AWS Control Tower. This will be referenced during the setup of the Control Tower service in Step 7.
Key Policy
```
{
    "Version": "2012-10-17",
    "Id": "CustomKMSPolicy",
    "Statement": [
        {
        ... YOUR-EXISTING-POLICIES ...
        },
        {
            "Sid": "Allow Config to use KMS for encryption",
            "Effect": "Allow",
            "Principal": {
                "Service": "config.amazonaws.com"
            },
            "Action": [
                "kms:Decrypt",
                "kms:GenerateDataKey"
            ],
            "Resource": "arn:aws:kms:YOUR-HOME-REGION:YOUR-MANAGEMENT-ACCOUNT-ID:key/YOUR-KMS-KEY-ID"
        },
        {
            "Sid": "Allow CloudTrail to use KMS for encryption",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": [
                "kms:GenerateDataKey*",
                "kms:Decrypt"
              ],
            "Resource": "arn:aws:kms:YOUR-HOME-REGION:YOUR-MANAGEMENT-ACCOUNT-ID:key/YOUR-KMS-KEY-ID",
            "Condition": {
                "StringEquals": {
                    "aws:SourceArn": "arn:aws:cloudtrail:YOUR-HOME-REGION:YOUR-MANAGEMENT-ACCOUNT-ID:trail/aws-controltower-BaselineCloudTrail"
                },
                "StringLike": {
                    "kms:EncryptionContext:aws:cloudtrail:arn": "arn:aws:cloudtrail:*:YOUR-MANAGEMENT-ACCOUNT-ID:trail/*"
                }
            }
        }
    ]
}
```

4. Create KMS Customer Managed Key (Symmetric, for Encrypt and Decrypt), KMS-CMK, for CloudWatch Log Groups. The arn of the key id is used as input into the CloudFormation script. 
Key Policy
```
{
    "Version": "2012-10-17",
    "Id": "key-consolepolicy-3",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::ACCOUNT-ID:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "logs.YOUR-HOME-REGION.amazonaws.com"
            },
            "Action": [
                "kms:Encrypt*",
                "kms:Decrypt*",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:Describe*"
            ],
            "Resource": "*"
        }
    ]
}
```

5. Set the environment variables in the Unix shell
    - AWS_ACCOUNT_ID --> set to the value of the management account
    - AWS_REGION --> set to the value of the "ap-southeast-1"
    - HOME_REGION --> set to the value of the "ap-southeast-5"
    - NOTE: HOME_REGION is required as temporary measure until Control Tower is available in Malaysia ap-southeast-5 region.
6. Run python scripts in management account in the following order:
    - Setup Organization OU folders, create Service Control Policies and attach to specific OUs. Execute this bash shell command "python3 organization-config.py"
    - Configure AWS account default security settings e.g. EBS Default Encryption, S3 block public access, EBS block public access, AMI block public access, EC2 IMDSv2 defaults and alternate security contact information. Execute this bash shell command "python3 account-config.py". 
    - Configure delegated administrator for each of these AWS Security Services (Security Hub, GuardDuty, Inspector, Firewall Manager). Certain services (Detective, Inspector, Firewall Manager) have been commented out contingent on the service's availability in the region. Execute this bash shell command "python3 security-config.py delegated_admin_account=123456789012"
7. Enable Control Tower in management account. Follow these instructions (TODO: specify link)
    - Enable IAM identity Center
    - Specify Region Deny, to only govern these regions (us-east-1, ap-southeast-1 and ap-southeast-2)
8. Login to new network account to run CloudFormation script "central-network-account.json". Name the new CloudFormation Stack name it as "central-network"


## Post CloudFormation deployment configuration
1. Set route to Firewall Endpoints in Route Tables
- NetworkInspection-Pub-A: 10.0.0.0/8 to firewall endpoint for that AZ-A
- NetworkInspection-Pub-B: 10.0.0.0/8 to firewall endpoint for that AZ-B
- NetworkInspection-Pub-C: 10.0.0.0/8 to firewall endpoint for that AZ-C
- NetworkInspection-TgwAttach-A: 0.0.0.0/0 to firewall endpoint for that AZ-A
- NetworkInspection-TgwAttach-B: 0.0.0.0/0 to firewall endpoint for that AZ-B
- NetworkInspection-TgwAttach-C: 0.0.0.0/0 to firewall endpoint for that AZ-C

2. Set up Transit Gateway Attachment in Spoke/Member VPCs to Network-Transit-Gateway

3. Set route and propagation to Spoke/Member VPCs 
- For Transit Gateway Route Table “Network-Main-Spoke” 
    - add Association to Workload-App-TgwAttach
- For Transit Gateway Route Table “Network-Main-Core” 
    - add Propagation for Workload-App-TgwAttach

4. Setup Firewall unmanaged rule group (Allow-Domains); set the source IP range to CIDRs of AWS VPCs or 10.25.0.0/16
```
.amazonaws.com
.amazon.com
```

5. Create a new unmanaged stateful firewall rule group (Stateful, Strict Order, Suricata) "custom-suricata-rule-group"
- Set Rule Group Format to Suricata
- Set Capacity to 10000
- Set IP set variables
	- "HOME_NET" to "10.25.0.0/16"
	- "ON_PREM_NET" to "on premise CIDR range"
- Set Port set variables
	- "ALLOW_ON_PREM_PORT" (22, 53, 123, 80, 443)
	- "ALLOW_PORT" (80, 443)
- Paste in the Suricata string from "firewall-suricata-rules.txt"

6. Add these to the firewall policy (central-network-StrictFirewallPolicy)
- Managed rules: ThreatSignaturesIOCStrictOrder, ThreatSignaturesExploitsStrictOrder, ThreatSignaturesMalwareWebStrictOrder
- Unmanaged rules: Allow-Domains, custom-suricata-rule-group 
- Priority sequence: Allow-Domains, ThreatSignaturesIOCStrictOrder, ThreatSignaturesExploitsStrictOrder, ThreatSignaturesMalwareWebStrictOrder, custom-suricata-rule-group

7. Configure the Transit Gateway routetable and propagation for the VPN connection that is attached to Transit Gateway

## Configure IAM Identity Center (IDC)
This will be used for all of the organization users to access the AWS environment.
1. Configure one of the accounts e.g. Shared Services account as the delegated administrator for IAM IDC. 
2. Configure these required IAM Permission Sets. (TODO: specify the permissions in table)
    - LZA-ProductionSupport-Access
    - LZA-Developer-Access
    - LZA-Security-Access
3. Configure the default identity directory to set MFA is required for all sign-ins. 

## Configure AWS Security Services
1. Login to the delegated administration account for security i.e. audit account.
2. Create a new Security Hub Central Configuration Policy that enabled "AWS Foundation Security Standards" across the governed regions (us-east-1, ap-southeast-1 and ap-southeast-2). 
    - Disable specific Security Hub findings that are no longer required.
        - [IAM.6] Hardware MFA should be enabled for the root user
3. Create an Event Pattern to send an automated email alert on CRITICAL or HIGH severity findings from Security Hub and GuardDuty products. Identify an email to subscribe to the SNS notification.
```
{
  "source": ["aws.securityhub"],
  "detail-type": ["Security Hub Findings - Imported"],
  "detail": {
    "findings": {
            "ProductArn": ["arn:aws:securityhub:ap-southeast-1::product/aws/guardduty", "arn:aws:securityhub:ap-southeast-1::product/aws/securityhub","arn:aws:securityhub:ap-southeast-5::product/aws/guardduty", "arn:aws:securityhub:ap-southeast-5::product/aws/securityhub"],
            "Severity": {
                "Label": ["CRITICAL", "HIGH"]
            }
        }
  }
}
```

## Configure AWS Systems Manager (SSM) for EC2 inventory management
1. Login to the delegated administration account for SSM.
1. Configure SSM Host Configuration Management Quick Start for the OUs (Workloads and Infrastructure). This ensures that all EC2 instances are managed by SSM Fleet Manager.
2. Enable "Default Host Configuration" from SSM Fleet Manager.

## Configure AWS Backup Plan and Policies
(TODO: Provide AWS Backup plan CloudFormation)
