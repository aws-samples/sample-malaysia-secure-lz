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
| Identity Access Management | IAM Identity Center | table | iam-config.yaml |
| Network Security | is 2nd | row | network-config.yaml |
| Security Assurance | Security Hub | ??? | security-config.yaml | 
| Threat Detection | GuardDuty | ? | security-config.yaml |
| Backup | is 3rd | row | organization-config.yaml, global-config.yaml |