# Jenkins Pipeline Fix Guide

This document explains how to fix the Docker push failure and other issues in the Jenkins pipeline.

## Problem Analysis

From the Jenkins logs, we can identify several issues:

1. **Docker Push Failure**: The pipeline fails at the "Push Image" stage
2. **Security Vulnerabilities**: Several dependencies have known vulnerabilities
3. **Kubernetes Configuration**: The kubeconfig points to localhost which won't work in Jenkins

## Fixes Applied

### 1. Security Vulnerabilities Fixed

Updated [app/requirements.txt](file:///home/prakuljain/yt/app/requirements.txt) to address:

- Werkzeug updated from 3.0.3 to 3.0.6 (fixes CVEs)
- Added explicit brotli version 1.0.9

### 2. Enhanced Error Handling

Improved Jenkinsfile with better error reporting:

- Credential validation before Docker login
- Image existence verification before push
- Detailed error messages with exit codes
- Better logging for debugging

### 3. Diagnostic Scripts Added

Created helper scripts for troubleshooting:

- `scripts/validate-docker-credentials.sh` - Validate Docker Hub credentials
- `scripts/diagnose-k8s-connectivity.sh` - Diagnose Kubernetes connectivity

## Steps to Fix the Docker Push Issue

### Step 1: Configure Docker Hub Credentials in Jenkins

1. Log into your Jenkins instance
2. Go to "Manage Jenkins" → "Manage Credentials"
3. Click on "Jenkins" under "Stores scoped to Jenkins"
4. Click on "Global credentials (unrestricted)"
5. Click "Add Credentials"
6. Set the following values:
   - Kind: "Username with password"
   - Scope: "Global"
   - Username: Your Docker Hub username
   - Password: Your Docker Hub access token (not your password)
   - ID: `docker-registry`
   - Description: "Docker Hub Credentials"
7. Click "OK"

### Step 2: Create Docker Hub Access Token

1. Log into Docker Hub
2. Go to "Account Settings" → "Security"
3. Click "New Access Token"
4. Give it a descriptive name like "Jenkins CI/CD"
5. Set permissions to "Read & Write"
6. Copy the generated token (this is your password for Jenkins)

### Step 3: Verify Docker Hub Configuration

Run the validation script to verify your credentials:

```bash
./scripts/validate-docker-credentials.sh YOUR_DOCKER_USERNAME YOUR_DOCKER_ACCESS_TOKEN
```

### Step 4: Update Repository Name (if needed)

If you're not using `prakuljain/yt-downloader` as your Docker Hub repository:

1. Update the Jenkinsfile environment section:

   ```groovy
   environment {
       DOCKER_HUB_REPO = "your-docker-hub-username/your-repository-name"
       // ... other variables
   }
   ```

2. Or use the parameter override:
   - In Jenkins, when building, set `DOCKER_REPO_OVERRIDE` to your repository

## Steps to Fix Kubernetes Deployment (Optional)

If you want to deploy to a real Kubernetes cluster:

### Step 1: Update kubeconfig-jenkins.yaml

Replace the placeholder values with your actual cluster information:

1. Update the server endpoint:

   ```yaml
   clusters:
     - cluster:
         server: https://your-actual-cluster-endpoint:port
         # ... other settings
   ```

2. Update the authentication token:
   ```yaml
   users:
     - name: jenkins-sa
       user:
         token: your-actual-service-account-token
   ```

### Step 2: Generate Service Account Token

If you need to generate a new token:

1. Create the service account and RBAC resources in your cluster:

   ```bash
   kubectl apply -f k8s/rbac.yaml
   ```

2. Generate a token using the helper script:
   ```bash
   ./scripts/generate-token.sh
   ```

### Step 3: Verify Kubernetes Connectivity

Run the diagnostic script:

```bash
./scripts/diagnose-k8s-connectivity.sh
```

## Re-running the Pipeline

After applying these fixes:

1. Trigger a new build in Jenkins
2. Monitor the "Push Image" stage for success
3. Check that subsequent stages (Deploy to Kubernetes, Health Check) now execute

## Additional Troubleshooting

If you continue to have issues:

1. Check Jenkins logs for detailed error messages
2. Verify network connectivity from Jenkins server to Docker Hub
3. Ensure your Docker Hub repository exists and is public or your credentials have access
4. Check that your Jenkins server has sufficient resources (disk space, memory)

## Security Best Practices

1. Always use access tokens instead of passwords for Docker Hub
2. Regularly rotate your access tokens
3. Monitor your Docker Hub account for unauthorized access
4. Keep dependencies updated to address security vulnerabilities
