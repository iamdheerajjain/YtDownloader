# Setting Up a Real Kubernetes Cluster

This guide explains how to configure the project to deploy to a real Kubernetes cluster instead of using the placeholder configuration.

## Prerequisites

1. A Kubernetes cluster (cloud provider or local)
2. kubectl CLI installed and configured
3. Proper authentication credentials for your cluster

## Step 1: Obtain Your Cluster Information

### For Cloud Providers:

#### AWS EKS:

1. Go to AWS Console → EKS → Your cluster
2. Note the API server endpoint
3. Download/update your kubeconfig with: `aws eks update-kubeconfig --name your-cluster-name`

#### Google GKE:

1. Go to Google Cloud Console → Kubernetes Engine → Clusters
2. Click on your cluster
3. Note the Endpoint URL
4. Get credentials with: `gcloud container clusters get-credentials your-cluster-name --zone=your-zone --project=your-project`

#### Azure AKS:

1. Go to Azure Portal → Kubernetes Services → Your cluster
2. Note the API server address
3. Get credentials with: `az aks get-credentials --resource-group your-resource-group --name your-cluster-name`

### For Local Clusters:

#### Minikube:

1. Start minikube: `minikube start`
2. Get the cluster info: `kubectl cluster-info`
3. The endpoint will typically be: `https://$(minikube ip):8443`

#### Kind:

1. Create a cluster: `kind create cluster --name your-cluster-name`
2. Get the cluster info: `kubectl cluster-info`
3. The endpoint will typically be: `https://127.0.0.1:xxxx`

## Step 2: Update kubeconfig-jenkins.yaml

Replace the placeholder values in `kubeconfig-jenkins.yaml` with your actual cluster information:

```yaml
apiVersion: v1
clusters:
  - cluster:
      certificate-authority-data: YOUR_REAL_CERTIFICATE_AUTHORITY_DATA
      server: https://YOUR-REAL-KUBERNETES-ENDPOINT
    name: production-cluster
contexts:
  - context:
      cluster: production-cluster
      namespace: youtube-app
      user: jenkins-sa
    name: jenkins-context
current-context: jenkins-context
kind: Config
users:
  - name: jenkins-sa
    user:
      token: YOUR-REAL-AUTHENTICATION-TOKEN
```

### Getting Certificate Authority Data:

- For cloud providers, this is usually in your downloaded kubeconfig file
- For local clusters, you can extract it with: `kubectl config view --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}'`

### Getting Authentication Token:

Depending on your cluster setup, you might use:

1. Service account token
2. Client certificate
3. Username/password
4. Other authentication methods

For service account token:

```bash
# Create a service account
kubectl create serviceaccount jenkins-deploy

# Create a role binding with appropriate permissions
kubectl create clusterrolebinding jenkins-deploy-binding --clusterrole=cluster-admin --serviceaccount=default:jenkins-deploy

# Get the token
kubectl get secret $(kubectl get sa/jenkins-deploy -o jsonpath="{.secrets[0].name}") -o go-template="{{.data.token | base64decode}}"
```

## Step 3: Configure RBAC Permissions

Ensure your Kubernetes user/service account has the necessary permissions:

```bash
# Create the service account
kubectl apply -f k8s/rbac.yaml
```

This creates:

- A service account named `jenkins-deploy`
- A role with permissions to manage deployments, services, pods, and configmaps
- A role binding that associates the service account with the role

## Step 4: Update Jenkins Pipeline (Already Done)

The Jenkinsfile has already been updated to use the real kubeconfig file instead of the placeholder one.

## Step 5: Test Your Configuration

Before running the full pipeline, test your kubeconfig locally:

```bash
# Set the kubeconfig
export KUBECONFIG=/path/to/your/project/kubeconfig-jenkins.yaml

# Test connection
kubectl cluster-info

# Test authentication
kubectl auth can-i create deployments --namespace youtube-app
```

## Security Considerations

1. Never commit real authentication tokens or certificates to version control
2. Store your kubeconfig file securely
3. Use dedicated service accounts with minimal required permissions
4. Rotate authentication tokens regularly

## Token Expiration

⚠️ **Important**: Kubernetes service account tokens may expire after 24 hours, depending on your cluster configuration. If your token expires, you'll need to generate a new one.

### Steps to Renew Expired Tokens

1. **Generate a new token** using the provided script:

   ```bash
   ./scripts/generate-token.sh
   ```

2. **Update your kubeconfig** with the new token:

   - Replace the token value in `kubeconfig-jenkins.yaml` under `users[0].user.token`
   - Or use the automated approach by running the script with the kubeconfig file path:

   ```bash
   ./scripts/generate-token.sh youtube-app jenkins-sa
   ```

3. **Verify the updated configuration**:

   ```bash
   ./scripts/validate-kubeconfig.sh
   ```

4. **Test connectivity**:
   ```bash
   kubectl --kubeconfig=kubeconfig-jenkins.yaml get pods -n youtube-app
   ```

### Automated Token Renewal

For production environments, consider implementing an automated token renewal process:

- Set up a cron job to regenerate tokens periodically
- Use Kubernetes secrets to store tokens securely
- Implement a notification system for token renewal events

## Troubleshooting

If you encounter issues:

1. Check that your cluster endpoint is reachable from your Jenkins server
2. Verify that your authentication token is valid and not expired
3. Ensure your service account has proper RBAC permissions
4. Use the validation script to check your kubeconfig structure
