# Malaysia SLZ Validation Agent (Experiment)

## Overview

**Validation agent** for the Malaysia Secure Landing Zone (SLZ). Performs compliance checks, prerequisite validation, and deployment readiness assessment. **Does NOT provision any AWS resources.**

## Quick Start

### Prerequisites

**1. AWS Credentials Setup (Read-Only Access)**

Configure AWS credentials with read-only permissions:

```bash
# Option 1: AWS SSO Login (For IAM Identity Center users)
aws configure sso
aws sso login --profile your-sso-profile

# Option 2: Configure with access keys (Legacy)
aws configure

# Verify credentials
aws sts get-caller-identity
```

**Required IAM Permissions (Read-Only):**
- Organizations: Describe*, List*, Get*
- CloudFormation: Describe*, List*, Get*
- IAM: Get*, List*
- KMS: Describe*, List*, Get*
- Control Tower: Describe*, List*, Get*
- GuardDuty, Security Hub, Inspector: Get*, List*, Describe*
- S3: List*, Get*
- EC2, VPC: Describe*
- STS: AssumeRole (for cross-account validation)

### Installation

```bash
# Copy agent configuration
cp slz-validation-agent.json ~/.kiro/agents/

# Start Kiro CLI in the SLZ repository
cd /path/to/lza-for-ps-malaysia
kiro-cli

# Select the agent
/agent swap slz-validation-agent

# Start validation
"Validate my AWS environment for SLZ deployment and come out with markdown report"
```

## What This Agent Does

### Multi-Account Validation
SLZ deploys resources across multiple accounts. The agent validates:
- **Management Account**: Organization, Control Tower, SCPs, RCPs, IAM Identity Center
- **Log-Archive Account**: CloudTrail logs, S3 access logs, SSM session logs
- **Audit Account**: GuardDuty (delegated admin), Security Hub, Inspector
- **Network Account**: VPC, Transit Gateway, Network Firewall, VPC endpoints
- **Shared Services Account**: Backup administration, IAM delegation
- **Central Backup Account**: Backup vaults
- **Member Accounts**: Account baseline (IAM password policy, EBS encryption, SSM)

**Cross-Account Access Methods:**
1. **IAM Identity Center (Recommended)**: User switches accounts via AWS access portal
2. **AssumeRole**: Agent assumes OrganizationAccountAccessRole from management account
3. **Manual Switch**: User re-authenticates to different accounts

**If you encounter AssumeRole permission issues:**
Use `aws sso login` to switch accounts manually and run validation per account:
```bash
# Validate management account
aws sso login --profile management
kiro-cli
/agent swap slz-validation-agent
"Validate management account"

# Switch to audit account
aws sso login --profile audit
kiro-cli
/agent swap slz-validation-agent
"Validate audit account"

# Repeat for each account: log-archive, network, shared-services, central-backup
```

### 1. Prerequisites Validation
Checks if environment is ready for SLZ deployment:
- AWS Organization structure
- Regions enabled (ap-southeast-5, us-east-1)
- Account status (no suspended accounts)
- S3 bucket for templates
- Existing security services status

### 2. CGSO Compliance Assessment
Validates compliance with 9 security domains:
- Identity Access Management (7.8.1, 7.5.7)
- Data Sovereignty (7.1.1, 7.2.1, 12.7.1)
- Data Protection (7.1.3, 12.1.1)
- Network Security (12.2.2, 12.4.2)
- Security Assurance (7.5.7, 12.1.2-12.1.5)
- Logging & Monitoring (7.3.1, 7.5.4, 12.3.3)
- Threat Detection (7.5.7, 12.4.2)
- Vulnerability Management (7.5.7, 12.4.2)
- Backup (7.5.5)

### 3. Existing Deployment Validation
For deployed SLZ environments across all accounts:
- CloudFormation stacks status
- Control Tower landing zone status
- Security services configuration
- SCPs and RCPs attachments
- IAM Identity Center setup
- Network resources
- Encryption settings
- Backup policies

### 4. Upgrade Readiness Assessment
For Control Tower upgrades:
- Identify custom SLZ policies
- Check policy attachments
- Validate Control Tower version
- Assess upgrade impact

### 5. Gap Analysis
Identifies missing or misconfigured resources:
- Required vs actual OUs
- Missing security services
- Unencrypted resources
- Non-compliant configurations

## What This Agent CANNOT Do

❌ Create, update, or delete AWS resources  
❌ Deploy CloudFormation stacks  
❌ Attach or detach policies  
❌ Enable or disable services  
❌ Modify configurations   

## What This Agent CAN Do

✅ Validate prerequisites  
✅ Check CGSO compliance  
✅ Assess deployment readiness  
✅ Identify gaps and issues  
✅ Provide recommendations  
✅ Reference documentation  
✅ Explain requirements  
✅ Generate validation reports  
✅ Save validation reports to local files  

## Saving Validation Reports

The agent can save validation reports to your local directory:

```bash
# Reports are saved to current working directory
# Example: validation-report-2026-02-21.md
```

**Report formats available:**
- Markdown (.md) - Human-readable format

## Version Information

- **Regions**: ap-southeast-5 (Malaysia), us-east-1 (N. Virginia)
- **CGSO Guidelines**: Malaysia public sector requirements
- **Agent Type**: Read-only validation
- **Agent Version**: 1.0.0
