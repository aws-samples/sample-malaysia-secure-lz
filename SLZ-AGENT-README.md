# Malaysia SLZ Deployment Agent (Preview)

## Overview

Specialized Kiro agent for deploying the **Malaysia Secure Landing Zone (SLZ)** for public sector organizations. Follows the deployment workbook in `cloudformation/readme.md` and uses AWS MCP servers to automate validation, deployment, and compliance verification.

## Quick Start

### Prerequisites

**1. AWS Credentials Setup (REQUIRED)**

Configure AWS credentials before using the agent:

```bash
# Option 1: AWS Login (Latest & Recommended - AWS CLI v2.32.0+)
aws login
# Opens browser for authentication, valid for 12 hours
# For cross-device: aws login --remote
# To logout: aws logout

# Option 2: AWS SSO Login (For IAM Identity Center users)
aws configure sso
aws sso login --profile your-sso-profile
export AWS_PROFILE=your-sso-profile

# Option 3: Configure with access keys (Legacy)
aws configure
# Enter: Access Key ID, Secret Access Key, Region (ap-southeast-5), Output format (json)

# Verify credentials
aws sts get-caller-identity
```

**Required IAM Permissions:**
- For `aws login`: Attach `SignInLocalDevelopmentAccess` managed policy to IAM user/role
- For deployments: Organizations, CloudFormation, IAM, KMS, Control Tower, GuardDuty, Security Hub, Inspector (Full access), S3 (Read/Write to template bucket)

### Installation

```bash
# Copy agent configuration
cp malaysia-slz-deployment-agent.json ~/.kiro/agents/

# Start Kiro CLI in the SLZ repository
cd /path/to/lza-for-ps-malaysia
kiro-cli

# Select the agent
/agent swap slz-agent

# Start deployment
"Help me deploy Malaysia Secure Landing Zone"
```

## What This Agent Does

### 1. Automated Validation
Uses `call_aws` to verify:
- AWS Organization structure
- Regions enabled (ap-southeast-5, us-east-1)
- Account status (no suspended accounts)
- S3 bucket for templates
- Existing resources

### 2. Deployment Guidance
Follows `cloudformation/readme.md` step-by-step:
1. Organization setup (lz-organization-setup.yaml)
2. Control Tower enablement with KMS encryption
3. Security service delegation (lz-delegate-security-services.yaml)
4. Organization guardrails - SCPs and RCPs (lz-organization-guardrails.yaml)
5. Account baseline via StackSet (lz-account-baseline.yaml)
6. IAM Identity Center permission sets (lz-iam-idc-permissionsets.json)
7. Central network setup (lz-central-network.json)
8. Security services (GuardDuty, Security Hub, Inspector)
9. Operations (SSM, Backup, CloudTrail)

### 3. Upgrade & Maintenance Support
Refers to `cloudformation/docs/upgrade.md` for:
- Control Tower version upgrades (e.g., v4.0)
- Policy detachment procedures before upgrades
- Post-upgrade validation steps
- Change log and release notes

**Example upgrade scenario:**
```
User: "I need to upgrade Control Tower to v4.0"

Agent:
1. References cloudformation/docs/upgrade.md
2. Identifies custom SLZ policies to detach
3. [call_aws] Lists attached SCPs and RCPs
4. Guides through detachment steps
5. Monitors Control Tower upgrade
6. Assists with post-upgrade validation
```

### 4. Real-Time Best Practices
Uses `aws___search_documentation` to:
- Search latest AWS documentation
- Find Control Tower setup guides
- Get Security Hub configuration steps
- Troubleshoot CloudFormation errors
- Check Control Tower upgrade procedures

### 5. CloudFormation Deployment
Uses `call_aws` to:
- Deploy stacks with correct parameters
- Monitor deployment progress
- Check stack events for errors
- Verify resources created

### 6. CGSO Compliance Verification
Validates all 9 security domains:
- Identity Access Management (7.8.1, 7.5.7)
- Data Sovereignty (7.1.1, 7.2.1, 12.7.1)
- Data Protection (7.1.3, 12.1.1)
- Network Security (12.2.2, 12.4.2)
- Security Assurance (7.5.7, 12.1.2-12.1.5)
- Logging & Monitoring (7.3.1, 7.5.4, 12.3.3)
- Threat Detection (7.5.7, 12.4.2)
- Vulnerability Management (7.5.7, 12.4.2)
- Backup (7.5.5)

## CloudFormation Templates

All templates in `cloudformation/` directory:

**Organization & Governance:**
- lz-organization-setup.yaml
- lz-organization-guardrails.yaml
- lz-organization-scp-guardrails.json
- lz-organization-scp-approved-services.json
- lz-organization-rcp-guardrails.json

**Security:**
- lz-delegate-security-services.yaml (StackSet)
- lz-audit-guardduty.yaml
- lz-audit-guardduty-notifications.yaml
- lz-audit-access-analyzer.json
- lz-delegate-firewall-manager-ipam.yaml

**Identity & Access:**
- lz-iam-idc-permissionsets.json
- lz-account-baseline.yaml (StackSet)

**Network:**
- lz-central-network.json
- lz-account-vpc-template.yaml
- network/firewall-suricata-rules.txt
- network/dns-malicious-domains.txt

## MCP Tools Used

### AWS API Server (`call_aws`)

### AWS Knowledge Server


## Example Interactions

### Starting Fresh Deployment
```
User: "Help me deploy Malaysia SLZ from scratch"

Agent:
1. [call_aws] Validates Organization: ✓ o-abc123xyz
2. [call_aws] Checks regions: ✓ ap-southeast-5 enabled
3. [call_aws] Lists accounts: 5 accounts found
4. [aws___search_documentation] Searches: "Control Tower setup"
5. Guides through prerequisites checklist
6. [call_aws] Collects Organization Root ID
7. Provides CloudFormation deployment command
8. [call_aws] Monitors stack creation
9. Verifies completion and guides to next step
```

### Troubleshooting Failed Stack
```
User: "My lz-organization-setup stack failed"

Agent:
1. [call_aws] Gets stack events and failure reason
2. [aws___search_documentation] Searches for error solution
3. Identifies root cause (e.g., missing KMS permissions)
4. Provides corrected configuration
5. Guides through retry process
```

### Compliance Verification
```
User: "Verify CGSO compliance"

Agent:
1. [call_aws] Checks IAM password policy: ✓
2. [call_aws] Verifies region deny SCP: ✓
3. [call_aws] Confirms EBS encryption: ✓
4. [call_aws] Validates CloudTrail: ✓
5. [call_aws] Checks GuardDuty: ✓
6. [call_aws] Verifies Security Hub: ✓
7. Reports: "All CGSO domains compliant"
```

## Cost Estimation

Baseline (8 accounts): **$2,000-2,500/month**

- Control Tower: $400
- GuardDuty: $300
- Network Firewall: $500
- Security Hub: $150
- Transit Gateway: $150
- VPC Endpoints: $200
- CloudTrail: $75
- Config: $150
- Others: $100

Reference: `cloudformation/malaysia_slz_cost_estimation_simple.md`

## Agent Configuration

**File:** `malaysia-slz-deployment-agent.json`

**MCP Servers:**
- `awslabs.aws-api-mcp-server` - AWS CLI execution (auto-approve: call_aws)
- `aws-knowledge-mcp` - AWS documentation (auto-approve: aws___search_documentation, aws___read_documentation, aws___get_regional_availability)

**Resources:**
- cloudformation/readme.md - Primary deployment guide
- cloudformation/docs/upgrade.md - Upgrade procedures and change log
- All CloudFormation templates
- Network configuration files
- Cost estimation report
- This README

## Workflow Pattern

1. **Read deployment guide** - Reference `cloudformation/readme.md`
2. **Validate prerequisites** - Use `call_aws` to check AWS resources
3. **Search best practices** - Use `aws___search_documentation`
4. **Collect parameters** - Use `call_aws` to get IDs and ARNs
5. **Deploy CloudFormation** - Use `call_aws` with template
6. **Monitor progress** - Use `call_aws describe-stack-events`
7. **Verify completion** - Use `call_aws` to validate resources
8. **Guide to next step** - Reference next step in readme.md

## Key Principles

- ✅ **Follow cloudformation/readme.md** - Authoritative deployment guide
- ✅ **Use MCP tools** - Validate and deploy via AWS APIs
- ✅ **Deploy sequentially** - Don't skip steps
- ✅ **Verify each phase** - Check resources before proceeding
- ✅ **CGSO compliance** - Validate all security domains
- ✅ **Recommend AWS Partner** - For complex network design

## Troubleshooting

### Common Issues

**CloudFormation stack failed:**
1. Get stack events: `call_aws describe-stack-events`
2. Search for solution: `aws___search_documentation`
3. Check Lambda logs if applicable
4. Provide remediation steps

**StackSet deployment failed:**
1. Check StackSet operations
2. Delete remaining CloudWatch Log Groups
3. Retry with corrected parameters

**Control Tower enrollment failed:**
1. Check for suspended accounts
2. Verify SCP attachments removed
3. Validate account email addresses

## Support Resources

- **Deployment Guide**: `cloudformation/readme.md`
- **Cost Estimation**: `cloudformation/malaysia_slz_cost_estimation_simple.md`
- **AWS Control Tower**: [User Guide](https://docs.aws.amazon.com/controltower/latest/userguide/)
- **AWS Organizations**: [User Guide](https://docs.aws.amazon.com/organizations/latest/userguide/)

## Version Information

- **Regions**: ap-southeast-5 (Malaysia), us-east-1 (N. Virginia)
- **CGSO Guidelines**: Malaysia public sector requirements
- **Templates**: 18 CloudFormation templates in `cloudformation/`
- **Agent Version**: 1.0.0
