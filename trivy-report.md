

# Trivy Docker Image Scan Report
Generated at: 2025-11-07 17:17:22.098333741 +0530 IST m=+3.098838336


---
## Target: Pipfile.lock
### Vulnerabilities
| Package | Vulnerability | Severity | Installed | Fixed | Title |
|----------|----------------|-----------|------------|--------|--------|
| flask-cors | CVE-2024-6221 | HIGH | 4.0.0 | 4.0.2 | A vulnerability in corydolphin/flask-cors version 4.0.1 allows the `Ac ... |
| gunicorn | CVE-2024-1135 | HIGH | 21.2.0 | 22.0.0 | python-gunicorn: HTTP Request Smuggling due to improper validation of Transfer-Encoding headers |
| gunicorn | CVE-2024-6827 | HIGH | 21.2.0 | 22.0.0 | gunicorn: HTTP Request Smuggling in benoitc/gunicorn |
| protobuf | CVE-2025-4565 | HIGH | 5.29.3 | 4.25.8, 5.29.5, 6.31.1 | python-protobuf: Unbounded recursion in Python Protobuf |
| waitress | CVE-2024-49768 | CRITICAL | 2.
1.2 | 3.0.1 | waitress: python-waitress: request processing race condition in HTTP pipelining with invalid first request |
| waitress | CVE-2024-49769 | HIGH | 2.1.2 | 3.0.1 | waitress: Waitress has a denial of service leading to high CPU usage/resource exhaustion |
## Target: package-lock.json
### Vulnerabilities
| Package | Vulnerability | Severity | Installed | Fixed | Title |
|----------|----------------|-----------|------------|--------|--------|
| axios | CVE-2025-27152 | HIGH | 1.7.9 | 1.8.2, 0.30.0 | axios: Possible SSRF and Credential Leakage via Absolute URL in axios Requests |
| axios | CVE-2025-58754 | HIGH | 1.7.9 | 1.12.0, 0.30.2 | axios: Axios DoS via lack of data size check |
| braces | CVE-2024-4068 | HIGH | 1.8.5 | 3.0.3 | braces: fails to limit the number of characters it can handle |
| braces | CVE-2024-4068 | HIGH | 2.3.2 | 3.0.3 | braces: fails to limit the number of characters it can handle |
| form-data | CVE-2025-7783 | CRITICAL | 4.0.0 | 2.5.4, 3.0.4, 4.0.4 | form-data: Unsafe random function in form-data |
| lodash | CVE-2021-23337 | HIGH | 4.17.20 | 4.17.21 | nodejs-lodash: command injection via template |
