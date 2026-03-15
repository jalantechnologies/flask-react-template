# DNS Setup Guide

This guide explains how to configure DNS records for your cluster deployment to enable SSL certificates and proper routing.

## Why DNS Setup is Required

When you deploy to a Kubernetes cluster, cert-manager needs to verify domain ownership via ACME HTTP-01 challenges. Without proper DNS records pointing to your cluster's ingress LoadBalancer, SSL certificates will fail to issue and your application will show certificate errors in browsers.

## Required DNS Records

For an application named `<app>` deployed at domain `<domain>` (e.g., app `operate-demo` at domain `bettrsw.com`), create the following A records pointing to your **nginx ingress LoadBalancer IP**:

| Record Name                                  | Type | Purpose                                |
| -------------------------------------------- | ---- | -------------------------------------- |
| `<app>.<domain>`                             | A    | Main application URL                   |
| `workers-dashboard.<app>.<domain>`           | A    | Workers dashboard (Temporal/Celery UI) |
| `preview.<app>.<domain>`                     | A    | Permanent preview environment          |
| `*.preview.<app>.<domain>`                   | A    | Per-PR preview environments            |
| `workers-dashboard.preview.<app>.<domain>`   | A    | Preview workers dashboard              |
| `*.workers-dashboard.preview.<app>.<domain>` | A    | Per-PR workers dashboards              |

> **Important:** Wildcard records (`*.preview.<app>.<domain>`) do NOT cover the apex name (`preview.<app>.<domain>`). You must add both explicitly.

## Example

For app `operate-demo` at domain `bettrsw.com` with LoadBalancer IP `203.0.113.50`:

```
operate-demo.bettrsw.com                                    A  203.0.113.50
workers-dashboard.operate-demo.bettrsw.com                  A  203.0.113.50
preview.operate-demo.bettrsw.com                            A  203.0.113.50
*.preview.operate-demo.bettrsw.com                          A  203.0.113.50
workers-dashboard.preview.operate-demo.bettrsw.com          A  203.0.113.50
*.workers-dashboard.preview.operate-demo.bettrsw.com        A  203.0.113.50
```

## How to Find Your LoadBalancer IP

### Option 1: kubectl get service

```bash
kubectl get svc -n ingress-nginx
```

Look for the `EXTERNAL-IP` of the `ingress-nginx-controller` service.

### Option 2: kubectl get ingress

```bash
kubectl get ingress -A
```

Check the `ADDRESS` column for any ingress resource.

### Option 3: DigitalOcean Console

1. Go to **Networking → Load Balancers**
2. Find the load balancer created by your cluster
3. Copy the IP address

## Verifying DNS Propagation

After adding DNS records, verify they're resolving correctly:

```bash
# Check main domain
dig +short <app>.<domain>

# Check preview domain
dig +short preview.<app>.<domain>

# Check wildcard
dig +short pr-123.preview.<app>.<domain>
```

All should return your LoadBalancer IP.

## Verifying Certificate Issuance

After DNS is configured, check that certificates are being issued:

```bash
# Check certificate status
kubectl get certificate -A

# Check for pending challenges
kubectl get challenges -A

# View cert-manager logs if issues persist
kubectl logs -n cert-manager -l app=cert-manager
```

Certificates should move from `Pending` to `Ready` within a few minutes.

## Troubleshooting

### Certificates Stuck in Pending

**Symptoms:**

- `kubectl get certificate` shows `Ready: False`
- Browser shows `NET::ERR_CERT_AUTHORITY_INVALID`
- nginx serves self-signed fallback certificate

**Solutions:**

1. **Verify DNS records are correct:**

   ```bash
   dig +short <your-domain>
   ```

   Should return your LoadBalancer IP.

2. **Check ACME challenges:**

   ```bash
   kubectl get challenges -A
   kubectl describe challenge <challenge-name> -n <namespace>
   ```

3. **Restart CoreDNS (if DNS was just added):**

   ```bash
   kubectl rollout restart deployment coredns -n kube-system
   ```

4. **Check cert-manager logs:**
   ```bash
   kubectl logs -n cert-manager -l app=cert-manager --tail=100
   ```

### DNS Not Propagating

- DNS changes can take 5-60 minutes to propagate globally
- Use `dig @8.8.8.8 <domain>` to check Google's DNS
- Clear local DNS cache: `sudo systemd-resolve --flush-caches` (Linux) or `sudo dscacheutil -flushcache` (macOS)

### Wrong LoadBalancer IP

If you recreated your cluster or ingress controller, the LoadBalancer IP may have changed. Update all DNS records with the new IP.

## When to Set Up DNS

DNS records should be configured:

1. **Before first deployment** - to avoid certificate errors
2. **After cluster creation** - once the ingress LoadBalancer is provisioned
3. **After cluster recreation** - if LoadBalancer IP changes

## Related Documentation

- [Deployment Guide](deployment.md)
- [Configuration](configuration.md)
- [cert-manager Documentation](https://cert-manager.io/docs/)
