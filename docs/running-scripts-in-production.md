# Running Scripts in Production

> ⚠️ **Warning:** Running scripts directly in the production environment can impact live users. Use this guide responsibly and with proper approvals.

This guide explains how to manually execute cron scripts inside the Kubernetes cluster for production when debugging or applying urgent fixes.

---

## 1. Prerequisites

Make sure the following tools are installed and accessible:

- [`doctl`](https://docs.digitalocean.com/reference/doctl/) – DigitalOcean CLI
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/) – Kubernetes CLI

> See [Developer Setup – CLI Tools](./deployment.md#developer-setup--cli-tools) if you're missing any tools.

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
