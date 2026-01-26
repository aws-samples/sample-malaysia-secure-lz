# Malaysia Secure Landing Zone - Upgrade & Change Log

This document provides upgrade instructions and change log for existing Malaysia Secure Landing Zone (SLZ) deployments.

---

## Change Log

| Date | Release | Description |
|------|---------|-------------|
| 30 January 2026 | [Control Tower Version 4.0 Upgrade](#30-january-2026---control-tower-version-40-upgrade) | Detach custom SLZ policies before upgrading to Control Tower v4.0 |

---

## Detailed Instructions

### 30 January 2026 - Control Tower Version 4.0 Upgrade

**Summary:** Before upgrading to AWS Control Tower version 4.0, you must detach custom SLZ policies to prevent conflicts with Control Tower guardrails.

**Why this is needed:** AWS Control Tower upgrades may introduce new guardrails that could conflict with existing SLZ Service Control Policies (SCPs) and Resource Control Policies (RCPs).

---

#### Identifying Custom SLZ Policies

The following are the custom SLZ policies that need to be detached before upgrading Control Tower.

**Custom SLZ Service Control Policies (SCPs):**

| Policy Name | Description |
|-------------|-------------|
| `my-slz-guardrail` | Baseline guardrail policy for data protection and security controls |
| `my-slz-approved-services` | Approved services guardrail policy limiting which AWS services can be used |

**Custom SLZ Resource Control Policies (RCPs):**

| Policy Name | Description |
|-------------|-------------|
| `my-slz-resource-guardrail` | Resource guardrail policy for S3 Block Public Access and TLS enforcement |

> **Note:** The actual policy names in your environment may vary depending on the values you specified during the initial SLZ deployment for the parameters `BaselineGuardrailPolicyName`, `ApprovedServicesPolicyName`, and `BaselineResourceGuardrailPolicyName`.

---

#### Step 1: Detach custom SLZ SCPs

1. Go to **AWS Organizations** → **Policies** → **Service control policies**
2. Click **`my-slz-guardrail`**
3. Go to **Targets** tab
4. Select all attached OUs/accounts/root
5. Click **Detach**
6. Repeat for **`my-slz-approved-services`**

> **Warning:** Do NOT detach the following policies:
> - **AWS managed policies** (e.g., `FullAWSAccess`)
> - **Policies prefixed with `aws-guardrails-*`** - these are managed by AWS Control Tower

---

#### Step 2: Detach custom SLZ RCPs

1. Go to **AWS Organizations** → **Policies** → **Resource control policies**
2. Click **`my-slz-resource-guardrail`**
3. Go to **Targets** tab
4. Select all attached OUs/accounts/root
5. Click **Detach**

> **Warning:** Do NOT detach the following policies:
> - **AWS managed policies** (e.g., `RCPFullAWSAccess`)
> - **Policies prefixed with `aws-guardrails-*`** - these are managed by AWS Control Tower

---

#### Step 3: Proceed with Control Tower Upgrade

1. Go to **AWS Control Tower** console
2. From side menu, click **Landing Zone setting**
2. Click **Update** or follow the upgrade process
3. Turn on automatic account enrollment 
4. Monitor upgrade completion
5. Review any errors or warnings during the upgrade

> **Note:** The upgrade process may take several minutes to complete. Do not navigate away from the console until the upgrade is finished.

---

#### Step 4: Post-Upgrade (After successful upgrade)

1. **Review Control Tower guardrails** now in place
   - Go to Control Tower → Controls
   - Review enabled detective and preventive controls

2. **Identify gaps** between Control Tower guardrails and your SLZ policies
   - Compare SLZ policy requirements with new Control Tower guardrails
   - Document any controls from SLZ not covered by Control Tower

3. **Re-attach custom policies** if still needed
   - Ensure no conflicts with Control Tower guardrails
   - Test in a non-production OU first
   - Attach to production OUs once validated

---