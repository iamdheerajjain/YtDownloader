#!/bin/bash

# Script to validate all fixes applied to resolve Jenkins pipeline issues
# Usage: ./scripts/validate-all-fixes.sh

set -e

echo "=== Validating All Fixes ==="
echo ""

# Check if requirements.txt has been updated
echo "1. Checking security updates in requirements.txt..."
if grep -q "Werkzeug==3.0.6" app/requirements.txt && grep -q "brotli==1.0.9" app/requirements.txt; then
    echo "✓ Security vulnerabilities in dependencies have been addressed"
else
    echo "✗ Security vulnerabilities may still exist in dependencies"
fi
echo ""

# Check if diagnostic scripts exist and are executable
echo "2. Checking diagnostic scripts..."
if [ -x "scripts/validate-docker-credentials.sh" ]; then
    echo "✓ Docker credential validation script exists and is executable"
else
    echo "✗ Docker credential validation script missing or not executable"
fi

if [ -x "scripts/diagnose-k8s-connectivity.sh" ]; then
    echo "✓ Kubernetes connectivity diagnosis script exists and is executable"
else
    echo "✗ Kubernetes connectivity diagnosis script missing or not executable"
fi
echo ""

# Check if documentation files exist
echo "3. Checking documentation files..."
if [ -f "docs/FIXES_SUMMARY.md" ] || [ -f "FIXES_SUMMARY.md" ]; then
    echo "✓ FIXES_SUMMARY.md exists"
else
    echo "✗ FIXES_SUMMARY.md missing"
fi

if [ -f "docs/JENKINS_FIX_GUIDE.md" ] || [ -f "JENKINS_FIX_GUIDE.md" ]; then
    echo "✓ JENKINS_FIX_GUIDE.md exists"
else
    echo "✗ JENKINS_FIX_GUIDE.md missing"
fi

if [ -f "docs/CHANGES_SUMMARY.md" ] || [ -f "CHANGES_SUMMARY.md" ]; then
    echo "✓ CHANGES_SUMMARY.md exists"
else
    echo "✗ CHANGES_SUMMARY.md missing"
fi
echo ""

# Check if Jenkinsfile has been updated with better error handling
echo "4. Checking Jenkinsfile improvements..."
if grep -q "LOGIN_STATUS" Jenkinsfile && grep -q "PUSH_STATUS" Jenkinsfile; then
    echo "✓ Jenkinsfile has enhanced error handling"
else
    echo "✗ Jenkinsfile may not have enhanced error handling"
fi
echo ""

# Check README updates
echo "5. Checking README updates..."
if grep -q "Recent Fixes and Improvements" README.md; then
    echo "✓ README.md has been updated with troubleshooting information"
else
    echo "✗ README.md may not have been updated with troubleshooting information"
fi
echo ""

echo "=== Validation Complete ==="
echo ""
echo "Next steps:"
echo "1. Configure Docker Hub credentials in Jenkins with ID 'docker-registry'"
echo "2. (Optional) Update kubeconfig-jenkins.yaml with actual cluster information"
echo "3. Re-run the Jenkins pipeline"
echo ""
echo "For detailed instructions, see docs/JENKINS_FIX_GUIDE.md"