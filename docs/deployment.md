# Temporal Deployment

We deploy **Temporal** using a Kubernetes-native setup to enable scalable, isolated background job execution for both preview and production environments.

---

## Key Details

### Per PR (Preview) Deployment

Each pull request triggers a temporary, isolated environment with:

- **Two Pods**:
  1. **WebApp Pod** – Runs:
     - React frontend
     - Flask backend
  2. **Temporal Pod** – Runs:
     - `python-worker` (via `temporal_server.py`)
     - `temporal-server`
     - `temporal-ui` (dashboard)

This ensures every PR runs its own background job workers independently of other deployments.

### Database

- A **PostgresSQL** database is shared across preview environments.
- Production uses a **dedicated** database.
- All credentials are securely managed via [Doppler](https://www.doppler.com/).

### Access Control

| Service           | Access Scope            |
|-------------------|-------------------------|
| `temporal-server` | Internal-only           |
| `temporal-ui`     | Public (preview + prod) |

### Temporal Server Address Resolution

- The environment variable `TEMPORAL_SERVER_ADDRESS` is dynamically resolved:
  - If **set in Doppler** → it uses that.
  - If **not set** → fallback to PR-specific or production address.

---

## Architecture Diagram

```
                ┌─────────────────────────────┐
                │    GitHub PR (Preview URL)  │
                │   e.g., pr-123.example.com  │
                └─────────────┬───────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │       Kubernetes Namespace (pr-123)     │
         └────────────────────┬────────────────────┘
                              |
                              │
                              │
                              │
   ┌────────────────────────────────────────────────────────────┐
   │                        Preview Pods                        │
   │                                                            │
   │            ┌───────────────────────────────┐               │
   │            │        WebApp Pod             │               │
   │            │  - React Frontend             │               │
   │            │  - Flask Backend              │               │
   │            └───────────────────────────────┘               │
   │                                                            │
   │      ┌──────────────────────────────────────────┐          │
   │      │         Temporal Services Pod            │          │
   │      │  -  python-worker (temporal_server.py)   │          │
   │      │  -  temporal-ui (Externally Exposed)     │          │
   │      │  -  temporal-server                      │          │
   │      └──────────────────────────────────────────┘          │
   │                                                            │
   └────────────────────────────────────────────────────────────┘
```

> Notes:
> - WebApp and Temporal services are separated for better scalability.
> - Docker networking is used for communication inside the Temporal pod.

📚 Learn more: [Temporal Deployment Docs](https://docs.temporal.io/application-development/foundations/deployment)

---

# Deployment Pipeline

Deployments are handled via **GitHub Actions** and [github-ci](https://github.com/jalantechnologies/github-ci).

- Preview deploys run per PR.
- Production deploys are triggered on merge to the main branch.



## Developer Setup – CLI Tools

Before deploying or debugging preview environments, ensure the following tools are installed based on your operating system:

### 1. `doctl` (DigitalOcean CLI)

**Windows:**
```sh
choco install doctl
```

**macOS:**
```sh
brew install doctl
```

**Linux:**
```sh
curl -s https://api.github.com/repos/digitalocean/doctl/releases/latest \
| grep "browser_download_url.*linux-amd64.tar.gz" \
| cut -d '"' -f 4 \
| wget -i - -O doctl.tar.gz

tar -xvzf doctl.tar.gz
sudo mv doctl /usr/local/bin/
```

### 2. `kubectl` (Kubernetes CLI)

**Windows:**
```sh
choco install kubernetes-cli
```

**macOS:**
```sh
brew install kubectl
```

**Linux:**
```sh
sudo apt update && sudo apt install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg

echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] \
https://apt.kubernetes.io/ kubernetes-xenial main" \
| sudo tee /etc/apt/sources.list.d/kubernetes.list > /dev/null

sudo apt update
sudo apt install -y kubectl
```

**Verify Installation**
```sh
doctl version
kubectl version --client
```

> ✅ Make sure both `doctl` and `kubectl` are accessible in your terminal before proceeding with preview or production deployment steps.

---

##  Per PR (Preview) Deployment

> Each new PR automatically creates a preview environment including:
> - a web app deployment
> - a dedicated Temporal server instance (running separately)

---

##  Manually Test Cron Scripts in Preview

To manually trigger the cron job inside the Preview environment:

### Step-by-step

1. **Install `doctl` and `kubectl`** to access the K8s cluster  
   - See [Developer Setup – CLI Tools](#-developer-setup--cli-tools)

2. **Login to DigitalOcean**
   - Navigate to the required DigitalOcean team (eg. `Platform`, `CaterPlan`, etc.)
   - Go to **API → Generate a new token**

3. **Run the following commands in terminal**:
```sh
doctl auth init --access-token <your-token>
doctl kubernetes cluster list
doctl kubernetes cluster kubeconfig save <cluster-name>
kubectl get ns
kubectl get pods -n <preview-namespace>
```

4. **Find the PR pod name** from the preview environment using `kubectl get pods`  
   (look for the name matching your PR deployment)

5. **Execute the cron script manually**:
```sh
kubectl exec -it <pod-name> -n <preview-namespace> -- /bin/bash
```
After entering the pod, you can run scripts like:
```sh
npm run run:change-booking-appointment-status
npm run run:send-appointment-reminder
```

This will immediately trigger the script **inside the running PR environment**, without waiting for the scheduled cron job.

---

## 📌 Notes

- If you face permission issues, ensure your DigitalOcean token has right access to the correct team and cluster.
- This manual trigger is only for debugging/testing and **should not** be used in production environments.
