#!/bin/bash
# Check for new vulnerabilities and enforce zero-tolerance policy
# Usage: ./check-new-vulnerabilities.sh <scan-failed> <new-critical> <new-high>

set -euo pipefail

SCAN_FAILED="$1"
NEW_CRITICAL="$2"
NEW_HIGH="$3"

echo "🔍 Checking scan results..."

# Verify scan completed successfully
if [ "$SCAN_FAILED" == "true" ]; then
    echo "❌ Scan failed to generate report!"
    exit 1
fi

# Default to 0 if values are empty
NEW_CRITICAL=${NEW_CRITICAL:-0}
NEW_HIGH=${NEW_HIGH:-0}

echo "  New CRITICAL vulnerabilities: $NEW_CRITICAL"
echo "  New HIGH vulnerabilities: $NEW_HIGH"

# Fail if ANY new HIGH or CRITICAL vulnerabilities found
if [ "$NEW_CRITICAL" -gt 0 ] || [ "$NEW_HIGH" -gt 0 ]; then
    echo ""
    echo "❌ Found new vulnerabilities!"
    [ "$NEW_CRITICAL" -gt 0 ] && echo "  - $NEW_CRITICAL new CRITICAL"
    [ "$NEW_HIGH" -gt 0 ] && echo "  - $NEW_HIGH new HIGH"
    echo ""
    echo "📋 Policy: Zero tolerance for new HIGH or CRITICAL vulnerabilities."
    echo "💬 Check the PR comment for detailed vulnerability information."
    exit 1
fi

echo "✅ No new vulnerabilities found"
exit 0
