#!/usr/bin/env python3
"""
Deploy-on-ZIP script for issue #69.

What it does
- Creates a new repo from your template (default: jalantechnologies/flask-react-template)
- Clones it locally (via gh CLI)
- Overlays the provided ZIP (AI-generated module or full app)
- Rewrites common placeholders to the new app name
- Commits & pushes to main
- Sets required GitHub Actions secrets & variables
- Triggers a dispatch-based deploy workflow
- Prints repo URL + Actions URL + computed preview hostname

Prereqs (installed + logged in)
- GitHub CLI (gh) with permission to create repos and set secrets/vars
- git
- docker (only for your CI runner; not needed locally)
- Kubernetes access is handled by your CI workflow—not by this script

Required env (per your platform)
Common:
  DOCKER_USERNAME="jalantechnologies"
  DOCKER_REGISTRY="registry.hub.docker.com"
  DOCKER_PASSWORD="<docker hub access token>"
  DOPPLER_PREVIEW_TOKEN="<doppler service token>"
Optional (Sonar):
  SONAR_HOST_URL="https://sonarqube.platform.jalantechnologies.com"
  SONAR_TOKEN="<sonar user token>"
Provider: choose ONE set

DigitalOcean:
  HOSTING_PROVIDER="DIGITAL_OCEAN"
  DO_ACCESS_TOKEN="<do pat>"
  DO_CLUSTER_ID="<terraform output do_cluster_id>"

AWS:
  HOSTING_PROVIDER="AWS"
  AWS_ACCESS_KEY_ID="..."
  AWS_SECRET_ACCESS_KEY="..."
  AWS_REGION="ap-south-1"   # change if needed
  AWS_CLUSTER_NAME="<terraform output eks_cluster_name>"

Usage
  ./deploy_from_zip.py --zip /path/to/app.zip \
    --app-name my-new-app \
    --org jalantechnologies \
    --provider do \
    --preview-domain "preview.platform.jalantechnologies.com"

Notes
- The template repo must include a workflow that listens to repository_dispatch 'deploy_on_zip'.
- If secrets/vars are missing, the script will list what’s missing and still finish repo creation.
"""

import argparse, os, sys, subprocess, shlex, tempfile, zipfile, secrets, json, pathlib, re

# ---------- shell helpers ----------
def sh(cmd, cwd=None, quiet=False):
    env = os.environ.copy()
    if isinstance(cmd, str):
        printable = cmd
        cmd = shlex.split(cmd)
    else:
        printable = " ".join(shlex.quote(x) for x in cmd)
    if not quiet:
        print("+", printable)
    subprocess.check_call(cmd, cwd=cwd, env=env)

def need(bin_name):
    from shutil import which
    if which(bin_name) is None:
        print(f"ERROR: '{bin_name}' is required on PATH")
        sys.exit(1)

def gen_name(): return "app-" + secrets.token_hex(4)

# ---------- zip extraction (safe) ----------
def safe_extract(zipf, dest):
    for m in zipf.namelist():
        if m.endswith("/"):  # directory
            continue
        # prevent path traversal
        dest_path = os.path.abspath(os.path.join(dest, m))
        if not dest_path.startswith(os.path.abspath(dest) + os.sep):
            print(f"WARNING: skipping suspicious path in zip: {m}")
            continue
        zipf.extract(m, dest)

# ---------- rewrite placeholders ----------
def rewrite_placeholders(repo_dir, app_name, preview_domain):
    root = pathlib.Path(repo_dir)

    # text replacements (include common variants)
    patterns = [
        (r"\bfrm-boilerplate\b", app_name),
        (r"\bboilerplate\b", app_name),
        (r"jalantechnologies/boilerplate", f"jalantechnologies/{app_name}"),
    ]

    skip_ext = {".png",".jpg",".jpeg",".ico",".pdf",".gz",".zip",".lock",".svg",".woff",".woff2"}
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() in skip_ext:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        orig = txt
        for pat, repl in patterns:
            txt = re.sub(pat, repl, txt)
        # sonar key / hostnames tweaks
        if p.name == "sonar-project.properties":
            txt = re.sub(r"(?m)^sonar\.projectKey\s*=.*$", f"sonar.projectKey={app_name}", txt)
        if txt != orig:
            p.write_text(txt, encoding="utf-8")

# ---------- gh secrets / vars ----------
def set_secret(repo, k, v): sh(['gh','secret','set',k,'-R',repo,'--body',v], quiet=True)
def set_var(repo, k, v):    sh(['gh','variable','set',k,'-R',repo,'-b',v], quiet=True)

# ---------- main ----------
def main():
    need("gh"); need("git")

    ap = argparse.ArgumentParser()
    ap.add_argument("-z","--zip", required=True, help="Path to application/module ZIP")
    ap.add_argument("--app-name", help="App/repo name (auto if omitted)")
    ap.add_argument("--org", default=os.getenv("GH_ORG","jalantechnologies"))
    ap.add_argument("--template", default=os.getenv("TEMPLATE_REPO","jalantechnologies/flask-react-template"))
    ap.add_argument("--provider", choices=["do","aws"], default=os.getenv("PROVIDER","do"))
    ap.add_argument("--preview-domain", default=os.getenv("PREVIEW_DOMAIN","preview.platform.jalantechnologies.com"))
    ap.add_argument("--skip-secrets", action="store_true", help="Don’t set secrets/vars (useful for dry-run)")
    ap.add_argument("--no-dispatch", action="store_true", help="Don’t trigger dispatch workflow")
    args = ap.parse_args()

    zpath = os.path.abspath(args.zip)
    if not os.path.exists(zpath):
        print("ERROR: ZIP not found:", zpath); sys.exit(1)

    name = args.app_name or gen_name()
    repo = f"{args.org}/{name}"
    preview_hostname = f"{name}.{args.preview_domain}"

    # 1) create repo from template
    sh(f"gh repo create {repo} --template {args.template} --private")

    # 2) clone, unzip, rewrite, commit, push
    with tempfile.TemporaryDirectory() as td:
        repo_dir = os.path.join(td, "repo")
        sh(["gh","repo","clone",repo,repo_dir])
        with zipfile.ZipFile(zpath) as zf:
            safe_extract(zf, repo_dir)
        rewrite_placeholders(repo_dir, name, args.preview_domain)

        sh("git add -A", cwd=repo_dir)
        sh(f'git commit -m "feat: add generated module {name}"', cwd=repo_dir)
        sh("git push origin main", cwd=repo_dir)

    # 3) set required GH Actions secrets/vars (mapped to your platform)
    missing = []
    if not args.skip_secrets:
        # common
        for key in ["DOCKER_USERNAME","DOCKER_REGISTRY","DOCKER_PASSWORD","DOPPLER_PREVIEW_TOKEN"]:
            if not os.getenv(key): missing.append(key)
        # optional sonar
        if os.getenv("SONAR_HOST_URL") and os.getenv("SONAR_TOKEN") is None:
            missing.append("SONAR_TOKEN")
        # provider
        if args.provider == "do":
            for key in ["HOSTING_PROVIDER","DO_ACCESS_TOKEN","DO_CLUSTER_ID"]:
                if not os.getenv(key): missing.append(key)
        else:
            for key in ["HOSTING_PROVIDER","AWS_ACCESS_KEY_ID","AWS_SECRET_ACCESS_KEY","AWS_REGION","AWS_CLUSTER_NAME"]:
                if not os.getenv(key): missing.append(key)

        if missing:
            print("\n[!] Missing env vars; skipping secrets/vars for these keys:")
            print("    " + ", ".join(sorted(set(missing))))
            print("    You can set them later in repo settings or re-run the script.")
        else:
            # common
            set_var(repo,    "DOCKER_USERNAME", os.environ["DOCKER_USERNAME"])
            set_var(repo,    "DOCKER_REGISTRY", os.environ["DOCKER_REGISTRY"])
            set_secret(repo, "DOCKER_PASSWORD", os.environ["DOCKER_PASSWORD"])
            set_secret(repo, "DOPPLER_PREVIEW_TOKEN", os.environ["DOPPLER_PREVIEW_TOKEN"])
            # optional sonar
            if os.getenv("SONAR_HOST_URL"):
                set_var(repo,    "SONAR_HOST_URL", os.environ["SONAR_HOST_URL"])
            if os.getenv("SONAR_TOKEN"):
                set_secret(repo, "SONAR_TOKEN", os.environ["SONAR_TOKEN"])
            # provider
            if args.provider == "do":
                set_var(repo,    "HOSTING_PROVIDER", os.environ["HOSTING_PROVIDER"])
                set_secret(repo, "DO_ACCESS_TOKEN",  os.environ["DO_ACCESS_TOKEN"])
                set_var(repo,    "DO_CLUSTER_ID",    os.environ["DO_CLUSTER_ID"])
            else:
                set_var(repo,    "HOSTING_PROVIDER", os.environ["HOSTING_PROVIDER"])
                set_secret(repo, "AWS_ACCESS_KEY_ID",     os.environ["AWS_ACCESS_KEY_ID"])
                set_secret(repo, "AWS_SECRET_ACCESS_KEY", os.environ["AWS_SECRET_ACCESS_KEY"])
                set_var(repo,    "AWS_REGION",            os.environ["AWS_REGION"])
                set_var(repo,    "AWS_CLUSTER_NAME",      os.environ["AWS_CLUSTER_NAME"])

    # 4) trigger repository_dispatch (requires a workflow listening for 'deploy_on_zip')
    if not args.no_dispatch:
        payload = {
            "event_type": "deploy_on_zip",
            "client_payload": {
                "provider": "do" if args.provider=="do" else "aws",
                "app_name": name,
                "app_hostname": preview_hostname
            }
        }
        # Using gh api to POST dispatch
        sh([
            "gh","api",f"repos/{repo}/dispatches",
            "--method","POST",
            "-H","Accept: application/vnd.github+json",
            "-f",f"event_type={payload['event_type']}",
            "-f",f"client_payload={json.dumps(payload['client_payload'])}"
        ])

    # 5) print result JSON
    print("\n=== RESULT ===")
    print(json.dumps({
        "appName": name,
        "repoUrl": f"https://github.com/{repo}",
        "actionsUrl": f"https://github.com/{repo}/actions",
        "previewUrl": f"https://{preview_hostname}",
        "next": "Watch Actions; when green, your Preview URL is live."
    }, indent=2))

if __name__ == "__main__":
    main()
