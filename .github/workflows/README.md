## Configuring Cloud Provider for CI/CD Workflows

This project supports deployment and cleanup on **both DigitalOcean and AWS** using GitHub Actions.  
You can easily switch the cloud provider for any environment by updating the `hosting_provider` input in the workflow files.

---

### How to Select the Cloud Provider

Each workflow file (such as `.github/workflows/production_on_push.yml`, `.github/workflows/preview_on_dispatch.yml`, `.github/workflows/clean_on_delete.yml`, etc.) contains a `hosting_provider` input.  

Set this value to choose your cloud provider:

- For **DigitalOcean**:  
  `hosting_provider: DIGITAL_OCEAN`
- For **AWS**:  
  `hosting_provider: AWS`

You can pass the `hosting_provider` value:
- **Directly** in the workflow `with:` block
- Or define it globally using **repository/environment variables** for easier management

**Example for DigitalOcean:**
```yaml
with:
  hosting_provider: DIGITAL_OCEAN
  # ...other inputs...
secrets:
  do_access_token: ${{ secrets.DO_ACCESS_TOKEN }}
  # ...other secrets...
```

**Example for AWS:**
```yaml
with:
  hosting_provider: AWS
  aws_cluster_name: <your-eks-cluster-name>
  aws_region: <your-aws-region>
  # ...other inputs...
secrets:
  aws_access_key_id: ${{ secrets.AWS_ACCESS_KEY_ID }}
  aws_secret_access_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  # ...other secrets...
```

---

### Required Inputs and Secrets

#### For DigitalOcean:
- **Inputs:**  
  - `do_cluster_id`
- **Secrets:**  
  - `do_access_token`

#### For AWS:
- **Inputs:**  
  - `aws_cluster_name`
  - `aws_region`
- **Secrets:**  
  - `aws_access_key_id`
  - `aws_secret_access_key`

---

### Steps to Change the Cloud Provider

1. **Open the workflow file** you want to update (e.g., `production_on_push.yml`).
2. **Change the value of `hosting_provider`** to either `DIGITAL_OCEAN` or `AWS`.
3. **Add or update the required inputs and secrets** for your chosen provider.
4. **Remove or comment out** any inputs/secrets not needed for your selected provider (optional, for clarity).
5. **Commit and push** your changes.

---

### Example: Switching from DigitalOcean to AWS

**Before (DigitalOcean):**
```yaml
with:
  hosting_provider: DIGITAL_OCEAN
  do_cluster_id: ${{ vars.DO_CLUSTER_ID }}
secrets:
  do_access_token: ${{ secrets.DO_ACCESS_TOKEN }}
```

**After (AWS):**
```yaml
with:
  hosting_provider: AWS
  aws_cluster_name: <your-eks-cluster-name>
  aws_region: <your-aws-region>
secrets:
  aws_access_key_id: ${{ secrets.AWS_ACCESS_KEY_ID }}
  aws_secret_access_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

### Notes

- The value for `hosting_provider` is **case-sensitive** and must match what the workflow expects.
- Make sure the required secrets are added in your GitHub repository settings under **Settings → Secrets and variables → Actions**.
- If you are using AWS, ensure your EKS cluster and IAM credentials are set up correctly.
- If you are using DigitalOcean, ensure your Kubernetes cluster and API token are set up correctly.

---