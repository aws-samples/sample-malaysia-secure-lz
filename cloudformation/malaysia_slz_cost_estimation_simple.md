# Malaysia Secured Landing Zone (SLZ) Cost Analysis Estimate Report

## Service Overview

The Malaysia Secured Landing Zone (SLZ) is designed for Malaysia public sector ministries, agencies (customers) and partners to deploy "Secure by Default" guardrails for their AWS multi-account landing zone. Malaysia Chief Government Security Officer (CGSO) cloud security requirements (where applicable) are transposed into configurable infrastructure as code (IaC) scripts. This comprehensive solution uses multiple AWS services following a pay-as-you-go pricing model, making it cost-effective for various government workloads.

## Pricing Model

This cost analysis estimate is based on the following pricing model:
- **ON DEMAND** pricing (pay-as-you-go) unless otherwise specified
- Standard service configurations without reserved capacity or savings plans
- No caching or optimization techniques applied

## Pricing Methodology

### Regions Used for Pricing
The pricing in this report is based on:
- **Primary Region**: Malaysia ap-southeast-5
- **Secondary Region**: US East (N. Virginia) us-east-1 for global services
- **Pricing Date**: As of May 2025

### How Pricing Was Obtained
1. **AWS Pricing Pages**: Official AWS service pricing pages (aws.amazon.com/pricing/)
2. **AWS Pricing Calculator**: Used for complex multi-service calculations
3. **AWS Documentation**: Confirmed regional pricing patterns for Asia Pacific regions

### Validation Method
To ensure accuracy, customers should:
1. Check the AWS Pricing Calculator with ap-southeast-5 selected
2. Review actual billing after deployment for any regional variations
3. Contact AWS sales for official quotes specific to Malaysia region

## Assumptions

- Minimum viable setup with 8 core AWS accounts:
  - Management Account (Organization root)
  - Audit Account (Security and compliance monitoring)
  - Log Archive Account (Centralized logging)
  - Shared Services Account (Shared tools and services)
  - Network Account (Centralized networking)
  - Central Backup Account (Backup management)
  - Production Account (Production workloads)
  - Non-Production Account (Development/testing)
- 2 AWS regions enabled: ap-southeast-5 (Malaysia) and us-east-1
- Average of 200 EC2 instances across all accounts
- 5TB of data processed through Network Firewall monthly
- 50GB of VPC Flow Logs and DNS logs for GuardDuty
- 500 configuration items per account for AWS Config
- Daily and weekly backup policies enabled
- 3 Availability Zones in use for Network Firewall
- 6 VPC endpoints for essential AWS services
- Standard workload patterns with moderate API usage

## Limitations and Exclusions

- Data transfer costs between regions
- EC2 instance costs
- Storage costs for S3 buckets (except backup storage)
- Third-party firewall appliances if chosen over AWS Network Firewall
- AWS Support plans
- Training and implementation costs
- Costs for optional services not yet enabled (Inspector, Detective, Firewall Manager)


### Cost Calculation - Minimum Usage (8 Core Accounts)

For organizations implementing the minimum viable Malaysia SLZ with 8 core accounts:

| Service | Usage | Calculation | Monthly Cost |
|---------|-------|-------------|-------------|
| AWS Control Tower & Organizations | Management of 8 AWS accounts across 2 regions (Management, Audit, Log Archive, Shared Services, Network, Central Backup, Production, Non-Production) | Control Tower and Organizations are free services | $0.00 |
| AWS GuardDuty | Threat detection across 8 accounts in 2 regions (Cloudtrail Events: 16 million events/month, Vpc Flow Logs: 200 GB/month, Dns Logs: 50 GB/month) | CloudTrail: 16M × $3.91/M = $62.56 + VPC/DNS logs: 250GB × $0.9775/GB = $244.38 + S3 Protection: 40M × $0.986/M = $39.44 + RDS Protection: 80 vCPUs × $1.037 = $82.96 = $429.34/month | $429.34 |
| AWS Security Hub | Security posture management for 8 accounts (Security Checks: 4,000 checks/month (500 per account), Finding Ingestion: 80,000 events/month, Automation Rules: 15 rules with 5 criteria) | Checks: 4K × $0.001 = $4 + Findings: 70K × $0.00003 = $2.10 + Rules: 12.6M × $0.13/M = $1.638 × 2 regions = $15.48/month | $15.48 |
| AWS Config | Configuration tracking for all resources (Configuration Items: 8,000 items/month (1000 per account), Rule Evaluations: 40,000 evaluations/month) | Config items: 8K × $0.003 = $24 + Rule evaluations: 40K × $0.001 = $40 × 2 regions = $128/month | $128.00 |
| AWS Network Firewall | Centralized firewall across 3 AZs with 5TB traffic (Endpoints: 3 endpoints (1 per AZ), Traffic: 5,000 GB/month) | Endpoints: 3 × $0.66 × 720 hours = $1,425.60 + Data: 5,000 GB × $0.065 = $325 = $1,750.60/month | $1,750.60 |
| AWS Transit Gateway | Central connectivity hub for VPCs (Attachments: 3 VPC attachments, Data Transfer: 500 GB/month) | Attachments: 3 × $0.06 × 720 hours = $129.60 + Data: 500 GB × $0.02 = $10 = $139.60/month | $139.60 |
| VPC Endpoints | Interface endpoints for AWS services (S3, SSM, EC2, etc.) (Endpoints: 6 interface endpoints × 3 AZs, Data Transfer: 200 GB/month) | Endpoints: 6 × 3 AZs × $0.01 × 720 hours = $129.60 + Data: 200 GB × $0.01 = $2 × 6 endpoints = $12 = $141.60/month | $141.60 |
| AWS KMS | Customer managed keys for encryption (Keys: 8 KMS keys (including replicas), Requests: 200,000 requests/month) | Keys: 8 × $1 = $8 + Requests: (200K - 20K free) × $0.03/10K = $0.54 × 2 regions = $9.08/month | $9.08 |
| AWS Backup | Centralized backup management (Ebs Backups: 2,000 GB, Efs Backups: 800 GB, Cross Region Copies: 400 GB) | EBS: 2,000 GB × $0.045 = $90 + EFS: 800 GB × $0.06 = $48 + Cross-region: 400 GB × $0.095 = $38 = $176/month | $176.00 |
| AWS CloudTrail | Organization-wide audit logging (Data Events: 20 million S3 events, Insights Events: 4 million events) | S3 data events: 20M × $0.10/100K = $20 + Insights: 4M × $0.35/100K = $14 + Additional trails = $2 = $36/month | $36.00 |
| AWS Systems Manager | EC2 fleet management and patching (Managed Instances: 200 instances, Parameter Requests: 400K/month, Patch Scans: 200 instances × 4 scans) | Parameters: 400K × $0.05/10K = $2 + Patching: No charge + Sessions: No charge = $2/month | $2.00 |
| AWS IAM Identity Center | Single sign-on for all accounts (Users: Unlimited, Applications: Unlimited) | IAM Identity Center is free | $0.00 |
| **Total** | **All services** | **Sum of all calculations** | **$2,827.70/month** |


## Cost Breakdown

### Unit Pricing Details

| Service | Resource Type | Unit | Price | Free Tier |
|---------|--------------|------|-------|------------|
| AWS Control Tower & Organizations | Control Tower | 1 unit | No charge | No additional charges for Control Tower and Organizations |
| AWS Control Tower & Organizations | Organizations | 1 unit | No charge | No additional charges for Control Tower and Organizations |
| AWS GuardDuty | Cloudtrail Events | million events | $3.91 | 30-day free trial for new accounts |
| AWS GuardDuty | Vpc Flow Logs | GB (first 500 GB) | $0.9775 | 30-day free trial for new accounts |
| AWS GuardDuty | S3 Protection | million events | $0.986 | 30-day free trial for new accounts |
| AWS GuardDuty | Eks Protection | million events | $1.8615 | 30-day free trial for new accounts |
| AWS GuardDuty | Rds Protection | vCPU/month | $1.037 | 30-day free trial for new accounts |
| AWS Security Hub | Security Checks | check (first 100K) | $0.001 | 30-day free trial available |
| AWS Security Hub | Finding Ingestion | event (after 10K free) | $0.00003 | 30-day free trial available |
| AWS Security Hub | Automation Rules | million evaluations | $0.13 | 30-day free trial available |
| AWS Config | Configuration Items | item | $0.003 | No free tier |
| AWS Config | Rule Evaluations | evaluation (first 100K) | $0.001 | No free tier |
| AWS Network Firewall | Endpoint Hourly | endpoint hour | $0.66 | No free tier |
| AWS Network Firewall | Data Processing | GB | $0.065 | No free tier |
| AWS Transit Gateway | Attachment Hourly | attachment hour | $0.06 | No free tier |
| AWS Transit Gateway | Data Processing | GB | $0.02 | No free tier |
| VPC Endpoints | Interface Endpoint | AZ hour | $0.01 | No free tier for interface endpoints |
| VPC Endpoints | Data Processing | GB | $0.01 | No free tier for interface endpoints |
| AWS KMS | Key Storage | key/month | $1.00 | 20,000 requests/month free tier |
| AWS KMS | Api Requests | 10,000 requests | $0.03 | 20,000 requests/month free tier |
| AWS Backup | Ebs Storage | GB-month | $0.045 | No free tier for backup storage |
| AWS Backup | Efs Storage | GB-month | $0.06 | No free tier for backup storage |
| AWS Backup | Cross Region | GB | $0.08-$0.11 | No free tier for backup storage |
| AWS CloudTrail | Management Events | 1 unit | First trail free | First trail free, data events charged |
| AWS CloudTrail | Data Events | 100,000 events | $0.10 | First trail free, data events charged |
| AWS CloudTrail | Insights | 100,000 events | $0.35 | First trail free, data events charged |
| AWS Systems Manager | Parameter Store | 10,000 requests | $0.05 | Basic features free, advanced features charged |
| AWS Systems Manager | Patch Manager | instance scan | No charge | No additional charges |
| AWS Systems Manager | Session Manager | 1,000 messages | No charge | No additional charges |
| AWS IAM Identity Center | Sso | 1 unit | No charge | No additional charges |


### Key Cost Factors

- **AWS Control Tower & Organizations**: Management of AWS accounts across regions
- **AWS GuardDuty**: Threat detection across accounts in multiple regions
- **AWS Security Hub**: Security posture management for all accounts
- **AWS Config**: Configuration tracking for all resources
- **AWS Network Firewall**: Centralized firewall across 3 AZs with traffic processing
- **AWS Transit Gateway**: Central connectivity hub for VPCs
- **VPC Endpoints**: Interface endpoints for AWS services (S3, SSM, EC2, etc.)
- **AWS KMS**: Customer managed keys for encryption
- **AWS Backup**: Centralized backup management
- **AWS CloudTrail**: Organization-wide audit logging
- **AWS Systems Manager**: EC2 fleet management and patching
- **AWS IAM Identity Center**: Single sign-on for all accounts


## Annual Cost Summary

Based on the minimum 8 accounts configuration:
- **Monthly Cost**: $2,827.70
- **Annual Cost**: $33,932.40
- **Cost per Account**: $353.46/month

## Conclusion

The Malaysia Secured Landing Zone provides comprehensive security and governance capabilities for AWS multi-account environments. The minimum viable setup with 8 core accounts has an estimated monthly cost of $2,827.70, covering essential security services, networking, backup, and compliance monitoring.
