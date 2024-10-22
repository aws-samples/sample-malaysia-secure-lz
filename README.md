# Landing Zone Accelerator (LZA) for PS Malaysia

Folder "beta-release" is a temporary set of scripts to deploy landing zone components using python scripts and Cloudformation scripts. This is required while waiting for AWS Control Tower and CodeDeploy are available for LZA deployments.

Folder "from-scratch" is the LZA configuration package with Service Control Policies, Default Security Guardrails and configuration. 

## Add your files
- [ ] [GitLab mwinit access guide](https://gitlab.pages.aws.dev/docs/Platform/ssh.html)
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin git@ssh.gitlab.aws.dev:ghazas/lza-for-ps-malaysia.git
git branch -M main
git add .
git commit -m "Initial Commit"
git push -uf origin main
```

## Technical requirements mapping to CGSO Cloud Guidelines

|Security Domain|Control Implementation|CGSO Control Reference|LZA Configuration|
| --- | --- | --- | --- |
| Identity Access Management | IAM Identity Center (Administrator, Developer, Security, Infrastructure OPerations, DevOps Permission Sets) | 7.8.1 | iam-config.yaml |
| Identity Access Management | IAM Password Policy | 7.5.7 | iam-config.yaml |
| Data Sovereignty | IAM Service Control Policy | 7.1.1, 7.2.1, 12.7.1 | iam-config.yaml |
| Data Protection | IAM Service Control Policy | 7.1.3 | iam-config.yaml |
| Data Protection | EC2 EBS Default Encryption | 12.1.1 | security-config.yaml |
| Data Protection | S3 Block Public Access | 12.1.1 | security-config.yaml |
| Network Security | VPC, Transit Gateway | 12.2.2 | network-config.yaml |
| Network Security | AWS Network Firewall with IPS (as Suricata rules) | 12.4.2 | network-config.yaml |
| Network Security | AWS Route53 DNS Resolver Firewall | 12.4.2 | network-config.yaml |
| Network Security | Centralized VPC interface endpoints (S3, DynamoDB, KMS, CloudWatch Log, Secrets Manager, EC2, SSM, SSM-Messages, ECR, GuardDuty)  | 7.1.3, 7.5.1 | network-config.yaml |
| Security Assurance | Security Hub | 7.5.7, 12.1.2, 12.1.3, 12.1.5 | security-config.yaml |
| Logging and Monitoring | Organization CloudTrail (multi-region, management events) | 7.3.1, 7.5.4, 12.3.3 | global-config.yaml | 
| Logging and Monitoring | SSM Session Manager | 7.3.1, 7.5.4 | global-config.yaml |
| Logging and Monitoring | S3 Access Logs | 7.3.1 | global-config.yaml |  
| Threat Detection | Amazon GuardDuty | 7.5.7, 12.4.2 | security-config.yaml |
| Vulnerability Management | Amazon Inspector | 7.5.7, 12.4.2 | security-config.yaml |
| Backup | Backup Vault and backup policies | 7.5.5 | organization-config.yaml, global-config.yaml |