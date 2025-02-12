# Malaysia LZA (Beta)

This beta release of the landing zone accelerator (LZA) is for Malaysia public sector agencies and partners to deploy "Secure by Default" guardrails for their AWS multi-account landing zone. CGSO cloud requirements are transposed into configurable infrastructure as code (IaC) scripts. 

![Malaysia Landing Zone Architecture](/cloudformation/images/malaysia-lza-presentation-lza.drawio.png)


Feature Components
1. Management: AWS Organization and Control Tower
    - Service Control Policy: region deny, enforce data encryption for data resources, and restrict access to approved AWS services.
    - Resource Policy: enforce TLS connections, prevent cross deputy
    - (optional) Control Tower Proactive controls can be configured by the customer
2. Logging: Control Tower using log-archive account
    - Organization CloudTrail
    - S3 Access Logs
    - BACKLOG: SSM Session Logs
    - BACKLOG: WAF Logs
    - BACKLOG: VPC Flow Logs
3. Security: Control Tower using audit account as the delegated security admin for GuardDuty, and Security Hub
    - Threat Detection: GuardDuty
    - Compliance Monitoring: Security Hub
    - BACKLOG: Vulnerability Patch Management: Inspector, with SSM Patch Manager Security Baseline
    - BACKLOG: Inspector, Detective, Firewall Manager (pending availability in region)
4. IAM: Control Tower IAM Identity Center (GA date unknown??) with identity federation to organization's Identity Provider (IdP). 
    - IAM Access Analyzer set Zone of Trust to "Organization" 
    - BACKLOG: Central Root management
5. Network: central network account, with ANFW and Route53 DNS Firewall, TGW and centralized VPC endpoints
    - VPC created subnets (app-private, db-private, public) across 3 availability zones.
    - Use VPC interface endpoints for privatelink access to AWS services (S3, SSM, SSMMessages, EC2, Log, KMS, Secrets Manager, ECR)
    - (optional) Customers can choose to deploy either AWS Network Firewall or their preferred network firewall e.g. Palo Alto or Fortinet as virtual appliances running as EC2 instances.
    - BACKLOG: Firewall Manager Policies (GA date unknown)
    - WAF: Baseline WAF configuration to attach to publicly accessible resources.
6. Backup: shared services account, and backup vault account 
    - Centrally managed using Control Tower Backup feature.
    - Backup policies (daily, weekly) configured and member accounts have local backup vaults. 
    - Backup policies move snapshots up to central backup vault at a later stage.
7. Block Public Access at account level: IMDSv2, AMI, Snapshots, S3
    - BACKLOG: VPC BPA
8. Compute Management: 
    - EC2: Default Host Configuration Management, EBS Default encryption with KMS-CMK, with SSM Quick Starts for Host Management and Resource Explorer
    - Containers: ECR has Inspector Enhanced Scanning 
    - Lambda: None
    - Aurora, RDS, EFS: enforce data-at-rest encryption with KMS-CMK
9. Forensics: OU


## Prerequisites:
Complete these validation checks before starting the deployment of the LZA. 
1. AWS management account has been created. 
2. AWS environment does not have any running workloads and services. 
3. All deny Service Control Policies (SCPs) and Resource Control Policies (RCPs) are detached from OUs.
4. Prepare separate emails for log-archive and audit accounts that will be created when Control Tower is initiated.
5. Create sharedservices account and backup-vault account that will be referenced during Control Tower Backup setup.
6. Disable existing AWS security services (Security Hub, Config, GuardDuty, Detective, Inspector) across all the regions. Remove delegated administration setting for each of the services. 
7. Enable opt-in Malaysia (ap-southeast-5) region from AWS Organization console.
8. Check for suspended accounts in the Organization. These would not be enrolled to Control Tower, and will be isolated under Suspended OU.
9. Customer needs to create a new repository in GitHub, GitLab or BitBucket to store the Malaysia LZA configuration pulled from (AWS source repo). 


## Installation Steps
1. *HOME-REGION* is Malaysia (ap-southeast-5).
2. Prepare an AWS Organization (without AWS Control Tower) in management account. Go to AWS Organization, and "Create an organization". Copy down the Organization ID, that will be used in subsequent steps.
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
2. Create the required Organization Units (OU) - Infrastructure, Workloads, Production, NonProduction, Forensic.
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-organization.json"
    - StackName: "lz-organization"
    - Parameters: Set the OrganizationRootId parameter to the AWS Organization Root OU.
3. Create required KMS-CMK key for AWS Control Tower (manual creation). Refer above for sample KMS-CMK key for AWS Control Tower. 
4. Create required KMS-CMK keys for CloudWatch Log Groups, Control Tower Backup and required IAM roles for Backup and SSM. Exception: Control Tower Backup feature requires KMS-CMK to be multi-region for management across multi-account and governed regions in a central backup vault. 
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-organization-kms-iam.json"
    - StackName: "lz-organization-kms-iam"
    - Parameters: Set the KeyAdministratorArn parameter to the permitted IAM Admin Role.
    - For the Control Tower Backup key, ensure to create a new replica key in us-east-1 and any other additional governed region. Go to KMS console, select the "control-tower-backup-key", go to "Regionality" and "Create new replica keys" for us-east-1.
5. Enable AWS Organization Trusted Access for selected services (GuardDuty, Security Hub, Inspector, Detective, Firewall Manager, IAM Access Analyzer, IAM, CloudFormation, Backup). 
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-organization-service-access.yaml"
    - StackName: "lz-organization-service-access"
6. Enable Control Tower in management account in Malaysia region. Follow these instructions from [AWS Control Tower quick start guide](https://docs.aws.amazon.com/controltower/latest/userguide/quick-start.html)
    - Create a log-archive account and an audit account as part of Control Tower implementation. 
    - Specify the KMS key id for Control Tower encryption
    - Specify Region Deny, to only govern these regions (us-east-1, and ap-southeast-5)
    - Enable Organization-Level CloudTrail
    - Set Log configuration for S3 to 1 year for both S3 retention and S3 access logging
    - Enable IAM Identity Center (IDC) in us-east-1 (pending availability in Malaysia region)
    - (Optional) Enable AWS Backup if the Shared Services account and BackupVault account are created. This can be optionally enabled later. 
    - Don't create another OU
7. Delegate security administration for AWS Security Services GuardDuty, Security Hub, Inspector, IAM Access Analyzer and Detective. 
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-delegate-native-security-services.yaml"
    - StackName: "lz-delegate-security-services"
    - Parameters: Set the AdminAccountId parameter to the AWS Control Tower audit account.
8. Delegate Firewall Manager security administration for centralized network management using policies. 
    - Deployment Region: N. Virginia us-east-1
    - CloudFormation script: "lz-delegate-firewall-manager.yaml"
    - StackName: "lz-delegate-firewall-manager"
    - Parameters: Set the AdminAccountId parameter to the AWS Control Tower audit account.    
9. Configure AWS Organization Service Control Policies (SCPs) with baseline, data-protection guardrails and approved services guardrails. Specify the target OUs to attach the SCPs to. 
    Baseline Guardrails
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-organization-scp-guardrails.json"
    - StackName: "lz-scp-baseline-guardrails"
    Approved Services
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-organization-scp-approved-services.json"
    - StackName: "lz-scp-approved-services"
10. Enable Resource Control Policies. Go to AWS Organizations --> Policies, and enable "Resource Control Policies"
11. Configure AWS Organization Resource Control Policies (RCPs). Ensure that Resource Control Policies is enabled at AWS Organization in management account before deploying RCPs. 
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-organization-rcp-guardrails.json"
    - StackName: "lz-rcp-baseline-guardrails"
    - Parameters: Set the MyOrganizationId parameter to the AWS Organization ID.
12. Enforce new AWS account security baseline for each member account in each home region. 
    - Enforce EBS Default Encryption with KMS-Customer Managed Key
    - Enforce Block Public Access for EBS snapshots
    - Enforce IMDS defaults as mandatory
    - BACKLOG: Set alternate security contact information
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-new-account-ec2-baseline.yaml"
    - StackName: "lz-account-baseline"
    - Parameters: Set the KeyAdministratorArn parameter to the permitted IAM Admin Role.
13. Enforce S3 Block Public Access at account level. Use the CloudFormation script "lz-s3-bpa.yaml", use StackName "lz-s3-bpa".
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-s3-bpa.yaml"
    - StackName: "lz-s3-bpa"
14. Enroll all the OUs (Infrastructure, Sandbox, Forensic) under Control Tower Management. Go to AWS Control Tower --> Organization and select the OU for registration. Do not register "Suspended" OU under Control Tower management because this is for closed/suspended accounts.
15. Configure AWS Backup for whole of organization. Skip this step if this was done at Step 6 under Control Tower setup.
    - Create new central backup account and backup administrator account under Infrastructure OU. 
    - Enable AWS Backup from Control Tower --> Landing Zone Settings --> Modify settings
16. Setup centralized networking account. 
    - Capture the OU to share the new Transit-Gateway resource. 
```
aws organizations describe-organizational-unit --organizational-unit-id <OU_ID> --query 'OrganizationalUnit.Arn'
```
    - Login to new network account to run CloudFormation script "lz-central-network.json". Name the new CloudFormation Stack name it as "lz-central-network". 6. Identify the OU identifer (format ou-XXXXXX) of the Infrastructure OU. 
 

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
2. Enable GuardDuty with auto-enable for organization and enable these protection plans for all the member accounts.
    - S3 Protection
    - Runtime Monitoring
    - Lambda Network Activity Monitoring
    - Malware Protection for EC2
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-audit-guardduty.yaml"
    - StackName: "lz-audit-guardduty"
3. Enable IAM Access Analyzer for organization to identify unused IAM resources and external access to your organization's resources i.e. S3, IAM Roles, KMS Keys. IAM Access Analyzer service role 'AWSServiceRoleForAccessAnalyzer' must be created in the organization management account before running this CloudFormation. 
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-audit-access-analyzer.yaml"
    - StackName: "lz-audit-access-analyzer"
4. Create a new Security Hub Central Configuration Policy that enabled "AWS Foundation Security Standards" across the governed regions (us-east-1, and ap-southeast-5). 
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
    - BUG: CloudFormation service in Malaysia region does not recognize AWS::SecurityHub::ConfigurationPolicy CloudFormation Resources. WORKAROUND: The above central configuration has to be done manually.
4. Create an Event Pattern to send an automated email alert on CRITICAL or HIGH severity findings from Security Hub and GuardDuty products. Identify an email to subscribe to the SNS notification.
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
1. Register SharedServices account as delegated administrator for Systems Manager Quick Setup. Go to AWS Systems Manager console in management account, choose Quick Setup and Settings, enter the SharedServices account for the delegated administrator. https://docs.aws.amazon.com/systems-manager/latest/userguide/quick-setup-register-delegated-administrator.html
2. Login to the SharedServices delegated administration account for SSM.
3. Configure SSM Quick Setup Host Management for these OUs (Workloads, Security and Infrastructure). This ensures that all EC2 instances are managed by SSM Fleet Manager.
    - Go to AWS Systems Manager console in management account, choose Quick Setup for Host Management.
    - Update Systems Manager (SSM) Agent every two weeks.
    - Collect inventory from your instances every 30 minutes.
    - Scan instances for missing patches daily.
    - Targets section should specify these OUs (Workloads, Security and Infrastructure) and governed home region (ap-southeast-5) for host management configuration to be deployed.
4. Configure SSM AWS Resource Explorer using Quick Setup. https://docs.aws.amazon.com/systems-manager/latest/userguide/Resource-explorer-quick-setup.html
    - Go to AWS Systems Manager console in management account, choose Quick Setup for Resource Explorer.
    - Set Aggregator Index Region to ap-southeast-5
    - Targets section should specify these OUs (Workloads, Security and Infrastructure) and governed home region (ap-southeast-5) 
5. Enable "Default Host Configuration" from SSM Fleet Manager. https://docs.aws.amazon.com/systems-manager/latest/userguide/fleet-manager-default-host-management-configuration.html

## Configure AWS Backup Plan and Policies
AWS Control Tower provides these 4 types of backup policies (hourly, daily, weekly and monthly), and each account that is under AWS Backup management will have its own Backup Vault. A Central Backup Vault "aws-controltower-central-backupvault-*" is created in the Central Backup Vault account. Resources in the member accounts need to be tagged with this one of these tags for it be include in the backup scope. https://docs.aws.amazon.com/controltower/latest/userguide/backup.html
- aws-control-tower-backuphourly: true
- aws-control-tower-backupdaily: true
- aws-control-tower-backupweekly: true
- aws-control-tower-backupmonthly: true

## Troubleshooting
1. CloudFormation deployment issues
- Go to AWS CloudFormation console, and select the Stack that has identified issues.
- Review the "Events" tab, and click on "View root cause" to identify the specific action that caused the failed deployment.
- Review the Lambda function's CloudWatch log group events to determine what may have caused the issues. Go to "Resources" tab and select the LambdaLogGroup to review the log stream events.

## Feature Backlog
1. Enable AWS Inspector for all accounts.
2. Enable AWS Firewall Manager and policies for all accounts.
3. Test using StackSets to automatically deploy lz-new-account-baseline.yaml in new accounts
