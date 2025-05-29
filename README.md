# Secure Landing Zone (SLZ) for Malaysia Public Sector

The Secure Landing Zone (SLZ) is for Malaysia public sector ministries, agencies (customers) and partners to deploy "Secure by Default" guardrails for their AWS multi-account landing zone. Malaysia Chief Government Security Officer (CGSO) cloud security requirements (where applicable) are transposed into configurable infrastructure as code (IaC) scripts. These scripts help customers and partners to accelerate their implementation at the early foundation stages of implementation.

## Technical requirements mapping to CGSO Cloud Guidelines

|Security Domain|Control Implementation|CGSO Control Reference|SLZ Configuration|
| --- | --- | --- | --- |
| Identity Access Management | IAM Identity Center (Administrator, Developer, Security, Infrastructure Operations, DevOps Permission Sets) | 7.8.1 | lz-iam-idc-permissionsets.json |
| Identity Access Management | IAM Password Policy | 7.5.7 | lz-account-baseline.yaml |
| Data Sovereignty | IAM Service Control Policy | 7.1.1, 7.2.1, 12.7.1 | lz-organization-scp-guardrails.json |
| Data Protection | IAM Service Control Policy | 7.1.3 | lz-organization-scp-guardrails.json |
| Data Protection | EC2 EBS Default Encryption | 12.1.1 | lz-account-baseline.yaml |
| Data Protection | S3 Block Public Access, enforce TLS for S3 | 12.1.1 | lz-organization-rcp-guardrails.json |
| Network Security | VPC, Transit Gateway | 12.2.2 | lz-central-network.json, lz-account-vpc-template.yaml |
| Network Security | AWS Network Firewall with IPS (as Suricata rules) | 12.4.2 | lz-central-network.json |
| Network Security | AWS Route53 DNS Resolver Firewall | 12.4.2 | PENDING |
| Network Security | Centralized VPC interface endpoints (S3, DynamoDB, KMS, CloudWatch Log, Secrets Manager, EC2, SSM, SSM-Messages, ECR, GuardDuty)  | 7.1.3, 7.5.1 | lz-central-network.json |
| Security Assurance | Security Hub | 7.5.7, 12.1.2, 12.1.3, 12.1.5 | Manual Configuration |
| Logging and Monitoring | Organization CloudTrail (multi-region, management events), as part of Control Tower | 7.3.1, 7.5.4, 12.3.3 | Manual Configuration | 
| Logging and Monitoring | SSM Session Manager | 7.3.1, 7.5.4 | Manual Configuration |
| Logging and Monitoring | S3 Access Logs | 7.3.1 | PENDING |  
| Threat Detection | Amazon GuardDuty | 7.5.7, 12.4.2 | lz-audit-guardduty.yaml, lz-audit-guardduty-notifications.yaml |
| Vulnerability Management | Amazon Inspector | 7.5.7, 12.4.2 | PENDING |
| Backup | Control Tower, Backup Vault and backup policies | 7.5.5 | Manual Configuration |


## Security
See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License
This library is licensed under the MIT-0 License. See the LICENSE file.
