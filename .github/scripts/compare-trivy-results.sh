#!/bin/bash
# Compare Trivy scan results between current PR and baseline (base branch)
# Usage: ./compare-trivy-results.sh <current-report.md> <baseline-report.json>

set -euo pipefail

CURRENT_REPORT="$1"
BASELINE_REPORT="$2"

# Validate scan report exists
if [ ! -f "$CURRENT_REPORT" ]; then
    echo "❌ Error: Scan report not found: $CURRENT_REPORT"
    echo "critical_count=0" >> "$GITHUB_OUTPUT"
    echo "high_count=0" >> "$GITHUB_OUTPUT"
    echo "total_count=0" >> "$GITHUB_OUTPUT"
    echo "new_critical=0" >> "$GITHUB_OUTPUT"
    echo "new_high=0" >> "$GITHUB_OUTPUT"
    echo "scan_failed=true" >> "$GITHUB_OUTPUT"
    exit 0
fi

# Count vulnerabilities in current PR
echo "📊 Analyzing current scan results..."
CRITICAL_COUNT=$(grep -E "^\| .+ \| CVE-.+ \| CRITICAL \|" "$CURRENT_REPORT" | wc -l | xargs || echo 0)
HIGH_COUNT=$(grep -E "^\| .+ \| CVE-.+ \| HIGH \|" "$CURRENT_REPORT" | wc -l | xargs || echo 0)
TOTAL_COUNT=$(grep -c "CVE-" "$CURRENT_REPORT" | xargs || echo 0)
echo "  Current: $CRITICAL_COUNT CRITICAL, $HIGH_COUNT HIGH (Total: $TOTAL_COUNT)"

# Count vulnerabilities in baseline (base branch)
BASELINE_CRITICAL=0
BASELINE_HIGH=0
if [ -f "$BASELINE_REPORT" ]; then
    echo "📊 Analyzing baseline scan results..."
    BASELINE_CRITICAL=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$BASELINE_REPORT" | xargs || echo 0)
    BASELINE_HIGH=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$BASELINE_REPORT" | xargs || echo 0)
    echo "  Baseline: $BASELINE_CRITICAL CRITICAL, $BASELINE_HIGH HIGH"
else
    echo "ℹ️  No baseline report - treating all vulnerabilities as new"
fi

# Calculate NEW vulnerabilities (delta = current - baseline)
NEW_CRITICAL=$((CRITICAL_COUNT - BASELINE_CRITICAL))
NEW_HIGH=$((HIGH_COUNT - BASELINE_HIGH))

# Ensure non-negative (if we fixed vulnerabilities, delta would be negative)
[ $NEW_CRITICAL -lt 0 ] && NEW_CRITICAL=0
[ $NEW_HIGH -lt 0 ] && NEW_HIGH=0

echo ""
echo "🔍 Comparison Results:"
echo "  New CRITICAL: $NEW_CRITICAL"
echo "  New HIGH: $NEW_HIGH"

# Output results for GitHub Actions
echo "critical_count=$CRITICAL_COUNT" >> "$GITHUB_OUTPUT"
echo "high_count=$HIGH_COUNT" >> "$GITHUB_OUTPUT"
echo "total_count=$TOTAL_COUNT" >> "$GITHUB_OUTPUT"
echo "new_critical=$NEW_CRITICAL" >> "$GITHUB_OUTPUT"
echo "new_high=$NEW_HIGH" >> "$GITHUB_OUTPUT"
echo "scan_failed=false" >> "$GITHUB_OUTPUT"

# Create GitHub Actions annotations
if [ "$NEW_CRITICAL" -gt 0 ]; then
    echo "::error::Found $NEW_CRITICAL new CRITICAL vulnerabilities"
elif [ "$NEW_HIGH" -gt 0 ]; then
    echo "::error::Found $NEW_HIGH new HIGH vulnerabilities"
elif [ "$TOTAL_COUNT" -gt 0 ]; then
    echo "::warning::Found existing vulnerabilities - no new issues introduced"
fi

echo ""
echo "✅ Analysis complete"
