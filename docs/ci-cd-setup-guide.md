# CI/CD Setup Guide

This guide provides detailed instructions for setting up the complete CI/CD pipeline using Git, Jenkins, and Kubernetes.

## Prerequisites

1. Jenkins server with required plugins:

   - Git Plugin
   - Docker Pipeline Plugin
   - Kubernetes CLI Plugin
   - Pipeline Utility Steps Plugin
   - Credentials Binding Plugin

2. Kubernetes cluster with kubectl access

3. Docker Hub account or private registry

4. Git repository hosting service (GitHub, GitLab, etc.)

## Jenkins Setup

### 1. Install Required Plugins

Navigate to **Manage Jenkins > Manage Plugins** and install:

- Git Plugin
- Docker Pipeline Plugin
- Kubernetes CLI Plugin
- Pipeline Utility Steps Plugin
- Credentials Binding Plugin

### 2. Configure Credentials

Go to **Manage Jenkins > Manage Credentials** and add:

1. **Docker Registry Credentials**

   - Kind: Username with password
   - ID: `docker-registry`
   - Username: Your Docker Hub username
   - Password: Your Docker Hub access token

2. **Kubernetes Configuration**
   - Kind: Secret file
   - ID: `kubeconfig-jenkins`
   - File: Upload your kubeconfig file

### 3. Configure Webhook (Optional)

To enable automatic pipeline triggering on Git commits:

1. In your Git repository settings, add a webhook:

   - URL: `http://your-jenkins-url/github-webhook/`
   - Content type: `application/json`
   - Events: Push events

2. For local development, use ngrok:
   ```bash
   ngrok http 8080
   ```
   Then use the provided URL as your webhook endpoint.

## Pipeline Configuration

### 1. Create Pipeline Job

1. In Jenkins, click **New Item**
2. Enter a name for your job
3. Select **Pipeline** and click OK
4. In the Pipeline section:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: Your repository URL
   - Credentials: Add Git credentials if repository is private
   - Script Path: `Jenkinsfile`

### 2. Pipeline Parameters

The pipeline supports the following parameters:

- `DEPLOY_ENVIRONMENT`: Target environment (development, staging, production)
- `RUN_TESTS`: Enable/disable unit tests
- `SKIP_DEPLOYMENT`: Skip deployment for testing

## Kubernetes Setup

### 1. Cluster Permissions

Ensure your Kubernetes cluster has the necessary permissions:

```bash
# Create namespace
kubectl create namespace youtube-app

# Apply RBAC
kubectl apply -f k8s/rbac.yaml
```

### 2. Configure kubeconfig

The kubeconfig file should contain valid user credentials to prevent interactive prompts:

```yaml
apiVersion: v1
clusters:
  - cluster:
      certificate-authority-data: <your-cert-data>
      server: <your-cluster-server>
    name: my-cluster
contexts:
  - context:
      cluster: my-cluster
      namespace: youtube-app
      user: jenkins-sa
    name: jenkins-context
current-context: jenkins-context
kind: Config
users:
  - name: jenkins-sa
    user:
      token: <your-service-account-token>
```

## Deployment Process

### 1. Manual Trigger

To manually trigger a build:

1. Go to your Jenkins job
2. Click **Build with Parameters**
3. Configure parameters as needed
4. Click **Build**

### 2. Automatic Trigger

When properly configured with webhooks, the pipeline will automatically trigger on:

- Push events to the repository
- Pull request merges

## Environment-Specific Deployments

The pipeline supports three environments:

- **Development**: `youtube-app-development`
- **Staging**: `youtube-app-staging`
- **Production**: `youtube-app`

Each environment gets its own namespace for isolation.

## Monitoring and Observability

The application exposes Prometheus metrics at `/metrics`:

- `download_requests_total`: Download request counter
- `download_duration_seconds`: Download duration histogram
- `health_check_requests_total`: Health check counter
- `active_requests`: Number of active requests
- `app_info`: Application information

## Troubleshooting

### Common Issues

1. **Docker Build Failures**

   - Check Docker daemon is running
   - Verify sufficient disk space
   - Ensure proper permissions

2. **Kubernetes Deployment Failures**

   - Check kubeconfig credentials
   - Verify cluster connectivity
   - Ensure RBAC permissions are applied

3. **Test Failures**
   - Check PYTHONPATH includes app directory
   - Verify all dependencies are installed

### Logs and Diagnostics

View Jenkins build logs for detailed information:

1. Go to your Jenkins job
2. Click on the build number
3. Click **Console Output**

For Kubernetes pod logs:

```bash
kubectl logs -n <namespace> -l app=youtube-api
```

## Security Considerations

1. **Credential Management**

   - Use Jenkins Credentials Store for all secrets
   - Rotate tokens regularly
   - Limit permissions to minimum required

2. **Container Security**

   - Run as non-root user
   - Regular security scanning
   - Keep base images updated

3. **Network Security**
   - Use network policies
   - Limit exposure through services
   - Enable TLS for external access

## Scaling and Performance

The application is configured with:

- Horizontal Pod Autoscaler (HPA) based on CPU usage
- Resource requests and limits
- Multiple replicas for high availability

To adjust scaling parameters, modify `k8s/hpa.yaml`.
