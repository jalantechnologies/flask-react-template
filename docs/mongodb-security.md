# MongoDB Security

## Why TLS Matters

MongoDB holds sensitive data: bcrypt-hashed credentials, account records, and application state. Without TLS, all traffic between the application and MongoDB travels in plaintext. Anyone on the same network segment — including other containers on a shared host, or an attacker who has achieved lateral movement — can read or modify that traffic. This is a requirement under SOC 2 CC6.7 and ISO 27001 A.10.1.

## URI Patterns That Satisfy the TLS Check

When a MongoDB connection is created outside development and testing, the app checks `MONGODB_URI` and logs a warning if TLS is absent. The following URI forms pass the check:

**MongoDB Atlas (SRV scheme — TLS is always on):**

```
mongodb+srv://user:pass@cluster.mongodb.net/dbname
```

**Self-hosted with TLS explicitly enabled:**

```
mongodb://host:27017/dbname?tls=true&tlsCAFile=/etc/ssl/mongo-ca.pem
```

**Legacy SSL parameter (accepted by the check, but `tls=true` is preferred):**

```
mongodb://host:27017/dbname?ssl=true
```

## How the Warning Works

`ApplicationRepositoryClient` validates the URI when it creates a MongoDB connection (in `modules/application/repository.py`, where `mongodb.uri` is read and the client is constructed). If the URI does not use the `mongodb+srv://` scheme and does not contain `tls=true` or `ssl=true` in the query string, a `WARN`-level log is emitted. This is intentionally non-fatal: TLS may be terminated at the network layer (e.g. a TLS-terminating proxy or service mesh) without appearing in the URI itself. The warning is the operator's cue to either add TLS parameters or confirm that the network layer provides equivalent protection.

The check is skipped when `APP_ENV` is `development` or `testing`.

## Encryption at Rest

### MongoDB Atlas

Encryption at rest is enabled by default on all Atlas tiers using AES-256. No operator action is required.

### Self-Hosted MongoDB

**Enterprise Edition:** Supports native encryption at rest via the WiredTiger storage engine. Enable it in `mongod.conf`:

```yaml
security:
  enableEncryption: true
  encryptionKeyFile: /etc/mongodb/encryption.key
```

**Community Edition:** Does not support WiredTiger encryption. Rely on volume-level encryption instead:

- **AWS:** encrypted EBS volumes (enable at volume creation or via the AWS console)
- **Linux (bare metal / VMs):** LUKS full-disk or volume encryption
- **Windows:** BitLocker

### Responsibility Boundary

The application configures the connection URI and warns about TLS at startup. Encryption at rest is the infrastructure / platform team's responsibility and cannot be enforced at the application layer.

## Self-Hosted Production Checklist

- TLS certificate issued for the MongoDB hostname (from a trusted CA or internal PKI)
- `net.tls.mode: requireTLS` set in `mongod.conf` to reject plaintext connections
- CA certificate available to the application container (`tlsCAFile` in the URI, or system trust store)
- Volume-level encryption enabled, or WiredTiger encryption configured (Enterprise)
- MongoDB user has least-privilege roles — avoid using the `root` user in production
- `authSource` in the URI matches the database where the user was created (typically `admin` for root-style init)

## Dev Environment

The dev `docker-compose.dev.yml` runs an unauthenticated MongoDB on the local network and points the app at `mongodb://app-db:27017/flask-react-template-dev` via `MONGODB_URI`. This is intentional for local development only and must never be used in production: bind production Mongo to a private network, require authentication, and enable TLS. The TLS warning is suppressed for `APP_ENV=development`.
