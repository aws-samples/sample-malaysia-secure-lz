# Malaysia SLZ (Beta)

This beta release of the Secure Landing Zone (SLZ) is for Malaysia public sector agencies and partners to deploy "Secure by Default" guardrails for their AWS multi-account landing zone. CGSO cloud requirements are transposed into configurable infrastructure as code (IaC) scripts. 

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
4. IAM: Control Tower IAM Identity Center with identity federation to organization's Identity Provider (IdP). 
    - IAM Access Analyzer set Zone of Trust to "Organization" 
    - Organization Central Root management
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
Complete these validation checks before starting the deployment of the SLZ. 
1. AWS management account has been created. 
2. Create an IAM user with Administrator access. Log in as this user.
3. Prepare an AWS Organization (without AWS Control Tower) in management account. Go to AWS Organization, and "Create an organization". Take note of the Organization ID (o-xxx), that will be used in subsequent installation steps.
4. Create a "Shared Services" account that is used for backup administration, IAM Identity Center administration delegation and other common cloud operation actions. This will be required during Control Tower Backup setup.
5. Create a "Central Backup" account that is used for the central storage of backups. This will be required during Control Tower Backup setup.
6. AWS environment does not have any running workloads and services. 
7. All deny Service Control Policies (SCPs) and Resource Control Policies (RCPs) are detached from OUs.
8. Prepare separate emails for log-archive and audit accounts that will be created when Control Tower is initiated.
9. Disable existing AWS security services (Security Hub, Config, GuardDuty, Detective, Inspector) across all the regions. Remove delegated administration setting for each of the services. 
10. Enable opt-in Malaysia (ap-southeast-5) region from AWS Organization console.
11. Check for suspended accounts in the Organization. These would not be enrolled to Control Tower, and will be isolated under Suspended OU.
12. Customer needs to create a new repository in GitHub, GitLab or BitBucket to store the Malaysia SLZ configuration pulled from (AWS source repo). 
13. Create an S3 Bucket for CloudFormation Templates in the Malaysia ap-southeast-5 region. 
    - Configure bucket settings:
        - Block all public access: Enabled (recommended)
        - Bucket versioning: Enabled (recommended)
        - Default encryption: Enabled (recommended)
    - Upload the below cloudformation templates into the S3 bucket. You can upload the files to the root of the bucket, or specify a prefix if templates are to be in a folder.
        - lz-organization.json
        - lz-organization-root-id.yaml
        - lz-organization-kms-iam.json
        - lz-organization-service-access.yaml
        - lz-organization-guardrails.json
        - lz-organization-scp-approved-services.json
        - lz-organization-rcp-guardrails.json


## Installation Steps
1. *HOME-REGION* is Malaysia (ap-southeast-5).
2. Create KMS Customer Managed Key (Symmetric, for Encrypt and Decrypt, single-region), KMS-CMK, for AWS Control Tower. This will be referenced during the setup of the Control Tower service in Step 7.
    - Region: Malaysia ap-southeast-5
    - Key Type: Symmetric Key
    - Key Usage: Encrypt and Decrypt.
    - Regionality: Single-Region
    - Alias: "control-tower-key"
    - Description: "KMS Key used by Control Tower service"
3. After creating the Control Tower KMS-CMK Key ("control-tower-key"), add the following SID statements to the "control-tower-key" key policy and replace the variables (HOME-REGION, YOUR-MANAGEMENT-ACOUNT-ID, YOUR-KMS-KEY-ID) accordingly.
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
1. Identify the AWS Organization identifer (format r-XXXXXX) from the AWS Organization console of the management account. This is an input parameter to the CloudFormation script "lz-organization-setup.yaml".
2. Create the required Organization Units (OU) - Infrastructure, Workloads, Production, NonProduction, Forensic, KMS-CMK Keys for CloudWatch Log Groups, Control Tower Backup and required IAM roles for Backup and SSM and AWS Organization Trusted Access for selected services (GuardDuty, Security Hub, Inspector, Detective, Firewall Manager, IAM Access Analyzer, IAM, CloudFormation, Backup)
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-organization-setup.yaml"
    - StackName: "lz-organization-setup"
    - Parameters: Set the OrganizationRootId parameter to the AWS Organization Root OU.
                  Set the KeyAdministratorArn parameter to the permitted IAM Admin Role.
                  Set the OrganizationId parameter to the AWS Organization ID.
    - NOTE: Do not change the stack-name to avoid conflict with following deployment steps.                  
3. For the Control Tower Backup key, ensure to create a new replica key in us-east-1 and any other additional governed region. Go to KMS console, select the "control-tower-backup-key", go to "Regionality" and "Create new replica keys" for us-east-1.
4. Enable AWS Organization Central Root Management. Go to IAM console, select "Account settings", and go to the section "Centralized root access for member accounts". 
    - Enable these capabilities 1) Root credentials management, and 2) Privileged root actions in member accounts.
    - Assign delegate administrator account to "Shared Services" account.
5. Enable Control Tower in management account in Malaysia ap-southeast-5 region. Follow these instructions from [AWS Control Tower quick start guide](https://docs.aws.amazon.com/controltower/latest/userguide/quick-start.html)
    - Deployment Region: Malaysia ap-southeast-5
    - Additional region for governance (for global services such as IAM, CloudFront, Route53): us-east-1
    - Specify Region Deny, to only govern these regions (us-east-1, and ap-southeast-5)
    - Foundational OU: Security 
    - Additional OU: Opt out of creating OU
    - Create a new log-archive account and a new audit account as part of Control Tower implementation. 
    - Specify the KMS key id for Control Tower encryption
    - Enable Organization-Level CloudTrail
    - Set Log configuration for S3 to 1 year for both S3 retention and S3 access logging
    - Enable IAM Identity Center (IDC) in Malaysia ap-southeast-5 region
    - Enable AWS Backup for whole of organization. Specify the new Shared Services (for backup administration) and central backup accounts. These accounts should not be enrolled under AWS Control Tower at the start.
        - Specify the KMS key id for Control Tower Backup encryption

6. Create Cloudformation Stackset to configure delegation of security administration for AWS Security Services GuardDuty, Security Hub, Inspector, IAM Access Analyzer and Detective. 
    - Deployment Region: ap-southeast-5
    - Create new CloudFormation Stackset
    - Permissions: Service-managed Permissions
    - Template: "lz-delegate-security-services.yaml"
    - StackSetName: lz-delegate-security-services
    - Parameters: Set the DelegatedSecurityAdminAccount parameter to the AWS Control Tower audit account.
    - Execution configuration: "Inactive"
    - Add stacks to stack set: "Deploy new stacks"
    - Set Deployment Targets: Deploy to organizational units (OUs), specify the root OU-ID. Set Account filter to "Intersection", and account number is the management account id.
    - Specify Regions: ap-southeast-5, us-east-1          

7. Enable Resource Control Policies. Go to AWS Organizations --> Policies, and enable "Resource Control Policies".

8. Enable Declarative Policies for EC2. Go to AWS Organizations --> Policies, and enable "eclarative Policies for EC2".

9. Configure AWS Organization Service Control Policies (SCPs) with baseline, data-protection guardrails, approved services guardrails and Resource Control Policies (RCPs). Ensure that Resource Control Policies is enabled at AWS Organization in management account before deploying RCPs. (Refer to previous steps) 
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-organization-guardrails.yaml"
    - StackName: "lz-organization-guardrails"
    Specify the parameters:
        - **S3BucketName**: Your S3 bucket name. Name of the bucket created in the pre-requisites where the cloudformation templates are uploaded.
        - **S3KeyPrefix**: Leave empty if templates are in the root of the bucket, or specify a prefix if templates are in a folder
        - **BaselineGuardrailPolicyName**: Name for the baseline guardrail policy (e.g., `my-slz-guardrail`)
        - **BaselineGuardrailPolicyDescription**: Description for the baseline guardrail policy
        - **ApprovedServicesPolicyName**: Name for the approved services policy (e.g., `my-slz-approved-services`)
        - **ApprovedServicesPolicyDescription**: Description for the approved services policy
        - **BaselineResourceGuardrailPolicyName**: Name for the resource guardrail policy (e.g., `my-slz-resource-guardrail`)
        - **BaselineResourceGuardrailPolicyDescription**: Description for the resource guardrail policy
        - **TargetOrganizationalUnitIds**: Comma-separated list of OU IDs to attach the policies to (e.g., `ou-abcd-1example,ou-efgh-2example`)
        - **TargetRootOrgIdforEC2Settings**: root organization ID (e.g., `r-abcd`)
        - **MyOrganizationId**: Your AWS Organization ID (e.g., `o-abcdefghij`)
    When executed, this template creates three child stacks in sequence, maintaining the proper order of operations required for effective policy implementation across your AWS Organization.

10. Create Cloudformation Stackset to configure new AWS account security baseline for each member account in each home region 
    - Deployment Region: Malaysia ap-southeast-5
    - Create new **"CloudFormation Stackset"**
    - Permissions: Service-managed permissions
    - Template: lz-account-baseline.yaml
    - StackSetName: "lz-account-baseline"
    - Parameters: Set the EbsDefaultEncryptionKeyAdministratorArn parameter to the permitted IAM Admin Role.
    - Specify Regions: ap-southeast-5, us-east-1
    - Deployment Configuration: "Deploy to Organization"


11. Enroll all the OUs (Infrastructure, Sandbox, Forensic) under Control Tower Management. Go to AWS Control Tower --> Organization and select the OU for registration. Do not register "Suspended" OU under Control Tower management because this is for closed/suspended accounts. Do not enable backup.

12. Enable IAM Access Analyzer in the management account that will create the IAM Access Analyzer service role 'AWSServiceRoleForAccessAnalyzer'. 
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-audit-access-analyzer.yaml"
    - StackName: "lz-audit-access-analyzer"
    - Parameter: 
        - AnalyzerType: ACCOUNT

13. Configure IAM Identity Center (IDC). IDC is used for all of the organization users to access the AWS environment for a single-sign-on experience.
    - Configure one of the accounts e.g. Shared Services account as the delegated administrator for IAM IDC. 
    - Configure these required IAM Permission Sets.
        - Deployment Region: Malaysia ap-southeast-5 region where IDC instance is deployed
        - CloudFormation script: "lz-iam-idc-permissionsets.json"
        - StackName: "lz-iam-idc-permissionsets"
    - (Optional) Configure your organization's Identity Provider (e.g. Microsoft EntraID, OKTA) to set MFA is required for all sign-in requests. 
    - Assign the IDC users with the required "SLZProductionSupportAccess" permission set to all the AWS accounts. This user will be used to configure the remaining steps in the member accounts.

| Permission Set Role | IAM Permissions | Description |
| ------------ | ------------ | ------------ |
| SLZProductionSupportAccess | PowerUserAccess | Used by Production Support team to work in production accounts. |
| SLZDeveloperAccess | ReadOnlyAccess, AmazonQDeveloperAccess, AWSCodeBuildDeveloperAccess, AmazonEC2FullAccess, AmazonS3FullAccess, AmazonDynamoDBFullAccess, AWSLambda_FullAccess, AmazonRDSFullAccess. AmazonSageMakerFullAccess, AmazonCloudWatchEvidentlyFullAccess | Used by Developers to work productively in development accounts. |
| SLZSecurityAccess | ReadOnlyAccess, AmazonGuardDutyFullAccess, AWSSecurityHubFullAccess, AmazonDetectiveFullAccess, AmazonInspector2FullAccess, AWSWAFConsoleFullAccess, AmazonAthenaFullAccess | Used by Security team to work productively on security services. | 

14. Setup centralized networking account. 
    - Create a new "Centralized Networking" account from Control Tower.
    - Identify the OU identifer (format ou-XXXXXX) to share the new Transit-Gateway resource with. This should be specified as the parameter in the format arn:aws:organizations::ACCOUNT-ID:ou/ROOT-OU-ID/INFRASTRUCTURE-OU-ID
    - Login to new network account to run CloudFormation script that deploys the VPC, AWS Network Firewall, Transit Gateway and Subnets. 
        - Deployment Region: Malaysia ap-southeast-5
        - CloudFormation script: "lz-central-network.json"
        - StackName: "lz-central-network"

15. Delegate Firewall Manager security administration for centralized network management using policies and IPAM Manager. 
    - Deployment Region: N. Virginia us-east-1
    - CloudFormation script: "lz-delegate-firewall-manager-ipam.yaml"
    - StackName: "lz-delegate-firewall-manager-ipam"
    - Parameters: Set the AdminAccountId parameter to the AWS Control Tower audit account.  
                  Set the DelegatedIPAMAdminAccount to the network account.         

## Post CloudFormation deployment configuration
Perform these configurations in central network account
1. Setup Firewall unmanaged rule group (Allow-Domains); set the source IP range to CIDRs of AWS VPCs or 10.25.0.0/16
```
.amazonaws.com
.amazon.com
```

2. Create a new unmanaged stateful firewall rule group (Stateful, Strict Order, Suricata) "custom-suricata-rule-group"
- Set Rule Group Format to Suricata
- Set Capacity to 10000
- Set IP set variables
	- "HOME_NET" to "10.25.0.0/16"
	- "ON_PREM_NET" to "on premise CIDR range"
- Set Port set variables
	- "ALLOW_ON_PREM_PORT" (22, 53, 123, 80, 443)
	- "ALLOW_PORT" (80, 443)
- Paste in the Suricata string from "firewall-suricata-rules.txt"

3. Add these rules to the firewall policy (lz-central-network-StrictFirewallPolicy)
- Managed rules: ThreatSignaturesIOCStrictOrder, ThreatSignaturesExploitsStrictOrder, ThreatSignaturesMalwareWebStrictOrder
- Unmanaged rules: Allow-Domains, custom-suricata-rule-group 
- Priority sequence: Allow-Domains, ThreatSignaturesIOCStrictOrder, ThreatSignaturesExploitsStrictOrder, ThreatSignaturesMalwareWebStrictOrder, custom-suricata-rule-group

4. Set route to Firewall Endpoints in Route Tables
- NetworkInspection-Pub-A: 10.0.0.0/8 to firewall endpoint for that AZ-A
- NetworkInspection-Pub-B: 10.0.0.0/8 to firewall endpoint for that AZ-B
- NetworkInspection-Pub-C: 10.0.0.0/8 to firewall endpoint for that AZ-C
- NetworkInspection-TgwAttach-A: 0.0.0.0/0 to firewall endpoint for that AZ-A
- NetworkInspection-TgwAttach-B: 0.0.0.0/0 to firewall endpoint for that AZ-B
- NetworkInspection-TgwAttach-C: 0.0.0.0/0 to firewall endpoint for that AZ-C

5. Set up Transit Gateway Attachment in Spoke/Member VPCs to Network-Transit-Gateway

6. Set route and propagation to Spoke/Member VPCs 
- For Transit Gateway Route Table “Network-Main-Spoke” 
    - add Association to Workload-App-TgwAttach
- For Transit Gateway Route Table “Network-Main-Core” 
    - add Propagation for Workload-App-TgwAttach

7. Configure the Transit Gateway routetable and propagation for the VPN connection that is attached to Transit Gateway

## Configure AWS Security Services
1. Enable Security Hub in management account for all the governed regions
    - Deployment Region: Malaysia ap-southeast-5, N. Virgina us-east-1
    - CloudFormation script: "lz-audit-securityhub.json"
    - StackName: "lz-organization-securityhub"
2. Login to the "Audit" account which is delegated security administration for the Control Tower landing zone.
3. Enable GuardDuty with auto-enable for organization and enable these protection plans for all the member accounts.
    - S3 Protection
    - Runtime Monitoring
    - Lambda Network Activity Monitoring
    - Malware Protection for EC2
    - Deployment Region: Malaysia ap-southeast-5
    - CloudFormation script: "lz-audit-guardduty.yaml"
    - StackName: "lz-audit-guardduty"
    - Add all the member accounts to the GuardDuty Protection Plan. Go to "GuardDuty" --> Accounts in delegated administration account for security. Select "Add Member" under "Actions"

4. Enable IAM Access Analyzer for organization to identify unused IAM resources and external access to your organization's resources i.e. S3, IAM Roles, KMS Keys. IAM Access Analyzer service role 'AWSServiceRoleForAccessAnalyzer' must be created in the organization management account before running this CloudFormation. 
- Deployment Region: Malaysia ap-southeast-5
- CloudFormation script: "lz-audit-access-analyzer.yaml"
- StackName: "lz-audit-access-analyzer"
- Parameter: 
    - AnalyzerType: ORGANIZATION

5. Create a new Security Hub Central Configuration Policy that enabled "AWS Foundation Security Standards" across the governed regions (us-east-1, and ap-southeast-5). 
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
6. In the "Audit" account, create an Event Pattern to send an automated email alert on CRITICAL or HIGH severity findings from Security Hub and GuardDuty products. Identify an email to subscribe to the SNS notification.
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

## Organization CloudTrail for S3 Data events
An Organization CloudTrail for S3 Data events is used to monitor and log access to S3 objects across all accounts in an AWS Organization, focusing on specific buckets or objects.
- Go to AWS CloudTrail in the AWS Console. Click Create trail.
- Under Trail name, enter a meaningful name
- Select Enable for my organization to apply the trail to all accounts.
- Choose the existing S3 bucket used to collect CloudTrail logs
- Configure KMS encryption for security.
- Under Event type, check Data events. Switch to Basic event selector
- Click S3 and choose either to trail for all bucker or specific S3 buckets.
- Configure CloudWatch Logs if monitoring is required.
- Review and Click Create trail.

## Troubleshooting
1. CloudFormation deployment issues
- Go to AWS CloudFormation console, and select the Stack that has identified issues.
- Review the "Events" tab, and click on "View root cause" to identify the specific action that caused the failed deployment.
- Review the Lambda function's CloudWatch log group events to determine what may have caused the issues. Go to "Resources" tab and select the LambdaLogGroup to review the log stream events and to identify the potential root causes.

2. CloudFormation rollback failure
- Go to AWS CloudFormation console and select the STack with the identified issues. 
- Force delete the StackSet and check the box to delete resources.
- Go to resources and check that all the previously created resources (e.g. IAM Role, Lamdba Function, CloudWatch Log Group) are moved. Click on each remaining resource, and delete the remaining resource manually. 

3. Control Tower Backup enrollment failure
- Error description "Insufficient privileges to create a backup vault. Creating a backup vault requires backup-storage and KMS permissions."
    - Review the KMS Key used for Control Tower Backup, to ensure that the region key replication is the same as Control Tower governed regions. 

## Feature Backlog
1. Enable AWS Inspector for all accounts.
2. Enable AWS Firewall Manager and policies for all accounts.
3. Test using StackSets to automatically deploy lz-new-account-baseline.yaml in new accounts
