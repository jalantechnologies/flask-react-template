# Running Scripts in Production

> ⚠️ **Warning:** Running scripts directly in the production environment can impact live users. Use this guide responsibly and with proper approvals.

This guide explains how to manually execute cron scripts inside the Kubernetes cluster for production when debugging or applying urgent fixes.

---

## 1. Prerequisites

Make sure the following tools are installed and accessible:

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

## 2. Authenticate with DigitalOcean and Connect to Kubernetes Cluster

1. **Login to DigitalOcean**
   - Navigate to the required DigitalOcean team (eg. `Platform`, `CaterPlan`, etc.)
   - Go to **API → Generate a new token**

2. **Authenticate using the token**:
   ```sh
   doctl auth init --access-token <your-production-token>
   doctl kubernetes cluster list
   doctl kubernetes cluster kubeconfig save <cluster-name>
   kubectl get ns
   ```

3. **Identify the pod** where your application is running:
   ```sh
   kubectl get pods -n <production-namespace>
   ```
4. **Open a shell session in the pod**:
```sh
kubectl exec -it <pod-name> -n <production-namespace> -- /bin/bash
```
5. **After entering the pod, you can run scripts like**:
```sh
npm run run:change-booking-appointment-status
npm run run:send-appointment-reminder
```
6. **Exit the pod shell when done**:

```sh
exit
```

## Best Practices
- Always double-check that you are in the correct production namespace.
- Only run scripts after validating the impact, ideally in preview first.
- Avoid running scripts that mutate critical state during peak traffic unless absolutely necessary.
