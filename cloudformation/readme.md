# Malaysia LZA (Beta)

This beta release of the landing zone accelerator (LZA) is for Malaysia public sector agencies and partners to deploy "Secure by Default" guardrails for their AWS multi-account landing zone. CGSO cloud requirements are transposed into configurable infrastructure as code (IaC) scripts. 

![Malaysia Landing Zone Architecture](/beta-release/images/malaysia-lza-presentation-lza.drawio.png)


Feature Components
1. Management: AWS Organization and Control Tower
    - Service Control Policy: region deny 
    - Resource Policy: enforce TLS connections, prevent cross deputy
    - (optional) Control Tower Proactive controls can be configured by the customer
2. Logging: Control Tower using log-archive account
    - SSM Session Logs
    - WAF Logs
    - VPC Flow Logs
3. Security: Control Tower using audit account as the delegated security admin for GuardDuty, Security Hub, Inspector, Firewall Manager
    - Threat Detection: GuardDuty
    - Compliance Monitoring: Security Hub
    - Vulnerability Patch Management: Inspector, with SSM Patch Manager Security Baseline
4. IAM: Control Tower IDC (GA date unknown) with identity federation to organization's IDP. 
    - IAM Access Analyzer set Zone of Trust to "Organization" 
    - Root management
5. Network: central network account, with ANFW and Route53 DNS Firewall, TGW and centralized VPC endpoints
    - Firewall Manager Policies (GA date unknown)
6. Backup: shared services account 
    - Backup policies at AWS Organization
7. Block Public Access at account level: VPC, IMDSv2, AMI, Snapshots, S3
8. Compute Management: 
    - EC2: Default Host Configuration Management, Default EBS encryption with KMS-CMK, with SSM Quick Starts for Host Management
    - Containers: ECR has Inspector Enhanced Scanning
    - Lambda: 
9. Forensics: OU


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
9. Customer needs to create a new repository in GitHub, GitLab or BitBucket to store the Malaysia LZA configuration pulled from (AWS source repo). AWS CodeConnections to connect and deploy to the target environment.


## Installation Steps
1. *HOME-REGION* is Malaysia (ap-southeast-5).
2. Prepare an AWS Organization (without AWS Control Tower) in management account. 
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


## Deployment Steps
1. Identify the AWS Organization identifer (format r-XXXXXX) from the AWS Organization console of the management account. This is an input parameter to the CloudFormation script "lz-organization.json".
2. Create the required Organization Units (OU) - Infrastructure, Workloads, Production, NonProduction, Forensic. Use the CloudFormation script "lz-organization.json", use StackName "lz-organization"
3. Create required KMS-CMK key for AWS Control Tower (manual creation). Refer above for sample KMS-CMK key for AWS Control Tower. 
4. Create required KMS-CMK keys for CloudWatch Log Groups and required IAM roles for Backup and SSM. Use the CloudFormation script "lz-organization-kms-iam.json"
5. Enable AWS Organization Trusted Access for selected services (GuardDuty, Security Hub, Inspector, Detective, Firewall Manager, IAM Access Analyzer, IAM, CloudFormation, Backup). Use the CloudFormation script "lz-organization-service-access.yaml", use StackName "lz-organization-service-access".
6. Enforce new AWS account security baseline for each member account in each home region. Use the CloudFormation script "lz-new-account-ec2-baseline.yaml", use StackName "lz-account-baseline"
    - Enforce EBS Default Encryption with KMS-Customer Managed Key
    - Enforce Block Public Access for EBS snapshots
    - Enforce IMDS defaults as mandatory
    - TODO: Set alternate security contact information
6. Identify the OU identifer (format ou-XXXXXX) of the Infrastructure OU. Capture the OU to share the new Transit-Gateway resource. 
aws organizations describe-organizational-unit --organizational-unit-id <OU_ID> --query 'OrganizationalUnit.Arn'
7. Enable Control Tower in management account in Malaysia region. Follow these instructions from [AWS Control Tower quick start guide](https://docs.aws.amazon.com/controltower/latest/userguide/quick-start.html)
    - Create a log-archive account and an audit account as part of Control Tower implementation. 
    - Specify the KMS key id for Control Tower encryption
    - Specify Region Deny, to only govern these regions (us-east-1, and ap-southeast-5)
    - Enable IAM Identity Center (IDC)
    - Don't create another OU
    - Don't enable AWS Backup (this will be done later)
8. Delegate security administration for AWS Security Services GuardDuty, Security Hub, Inspector, Firewall Manager, IAM Access Analyzer and Detective. Use the CloudFormation script "lz-delegate-native-security-services.yaml", use StackName "lz-delegate-security-services". Set the AdminAccountId parameter to the AWS Control Tower audit account.
9. Configure AWS Organization Service Control Policies (SCPs) with baseline, data-protection guardrails and approved services guardrails. Specify the target OUs to attach the SCPs to. Use the CloudFormation scripts "lz-scp-baseline-guardrail.json", "lz-scp-data-guardrail.json", and "lz-scp-approved-services.json". use StackName "lz-scp-baseline-guardrails", "lz-scp-data-protection-guardrails", "lz-scp-approved-services" respectively.
10. Configure AWS Organization Resource Control Policies (RCPs). Ensure that Resource Control Policies is enabled at AWS Organization in management account before deploying RCPs. Use the CloudFormation script "lz-organization-rcp-guardrails.json", use StackName "lz-rcp-baseline-guardrails".
11. Login to new network account to run CloudFormation script "central-network-account.json". Name the new CloudFormation Stack name it as "central-network"


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
1. Login to the delegated administration account for security i.e. Control Tower audit account.
2. Create a new Security Hub Central Configuration Policy that enabled "AWS Foundation Security Standards" across the governed regions (us-east-1, ap-southeast-1 and ap-southeast-2). 
    - Disable specific Security Hub findings that are no longer required.
        - [IAM.6] Hardware MFA should be enabled for the root user
        - [ELB.2] Classic Load Balancers with SSL/HTTPS listeners should use a certificate provided by AWS Certificate Manager
        - [ELB.3] Classic Load Balancer listeners should be configured with HTTPS or TLS termination
        - [ELB.7] Classic Load Balancers should have connection draining enabled
        - [ELB.8] Classic Load Balancers with SSL listeners should use a predefined security policy that has strong AWS Configuration
        - [ELB.9] Classic Load Balancers should have cross-zone load balancing enabled
        - [ELB.10] Classic Load Balancer should span multiple Availability Zones
        - [ELB.14] Classic Load Balancer should be configured with defensive or strictest desync mitigation mode
        - [Macie.1] Amazon Macie should be enabled
        - [Macie.2] Macie automated sensitive data discovery should be enabled
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
