# 🎬 YouTube Playlist Downloader API

A Flask-based REST API for retrieving YouTube video information with a complete CI/CD pipeline using Git, Jenkins, and Kubernetes.

## ✨ Features

- 🎥 Retrieve YouTube video information without downloading
- 📊 Built-in Prometheus metrics for monitoring
- 🐳 Docker containerization
- ⚡ Kubernetes deployment with autoscaling
- 🔄 Automated CI/CD pipeline with Jenkins
- 🛡️ Health and readiness probes
- 📈 Horizontal Pod Autoscaler (HPA)
- 🚀 Automatic build triggering on Git commits
- 🌐 Multi-repository and multi-cluster support

## 📋 Requirements

- Python 3.6 or higher
- Docker
- Kubernetes cluster
- Jenkins server
- FFmpeg (for video processing)

## 🚀 Quick Start

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd yt-downloader
   ```

2. **Run locally:**

   ```bash
   pip install -r app/requirements.txt
   python app/main.py
   ```

3. **Access the API:**
   - API Root: http://localhost:2000/
   - Health Check: http://localhost:2000/health
   - Readiness Check: http://localhost:2000/ready
   - Metrics: http://localhost:2000/metrics

## 🏗️ CI/CD Pipeline

This project includes a complete CI/CD pipeline implemented with Jenkins:

### Pipeline Stages

1. **Checkout** - Clones source code from Git
2. **Code Quality** - Runs static analysis (extensible)
3. **Unit Tests** - Executes test suite
4. **Docker Build** - Creates container image
5. **Security Scan** - Scans for vulnerabilities
6. **Push Image** - Uploads to container registry
7. **Deploy to K8s** - Deploys to Kubernetes cluster
8. **Health Check** - Verifies deployment

### Pipeline Parameters

- `DEPLOY_ENVIRONMENT` - Target environment (development, staging, production)
- `RUN_TESTS` - Enable/disable unit tests
- `SKIP_DEPLOYMENT` - Skip deployment for testing
- `DOCKER_REGISTRY_OVERRIDE` - Override default Docker registry
- `DOCKER_REPO_OVERRIDE` - Override default Docker repository
- `NAMESPACE_OVERRIDE` - Override default Kubernetes namespace base name
- `DEPLOYMENT_OVERRIDE` - Override default deployment name

### Automatic Build Triggering

The pipeline automatically triggers on Git push events. To set this up:

1. In your Git repository settings, add a webhook:

   - URL: `http://your-jenkins-url/github-webhook/`
   - Content type: `application/json`
   - Events: Push events

2. For local development, use ngrok:
   ```bash
   ngrok http 2000
   ```
   Then use the provided URL as your webhook endpoint.

## 🐳 Docker Support

The application is containerized using a multi-stage Dockerfile:

```bash
# Build the image
docker build -t yt-downloader .

# Run the container
docker run -p 2000:8080 yt-downloader
```

## ☸️ Kubernetes Deployment

Kubernetes manifests are provided for deployment:

```bash
# Apply all manifests
kubectl apply -f k8s/

# Or use the deployment script
./scripts/k8s-deploy.sh kubeconfig-jenkins.yaml youtube-app youtube-api prakuljain/yt-downloader:latest
```

### Components

- **Deployment** - Manages application pods
- **Service** - Exposes application internally
- **HPA** - Automatically scales based on CPU usage
- **RBAC** - Secure access controls
- **Namespace** - Isolated environment

### Setting Up a Real Kubernetes Cluster

By default, the project uses a placeholder kubeconfig for demonstration purposes. To deploy to a real Kubernetes cluster:

1. Follow the detailed instructions in [REAL_CLUSTER_SETUP.md](REAL_CLUSTER_SETUP.md)
2. Update `kubeconfig-jenkins.yaml` with your actual cluster endpoint and authentication credentials
3. Ensure your Jenkins server can reach the Kubernetes API endpoint
4. Configure proper RBAC permissions for the Jenkins service account

## 🧪 Testing

Run unit tests with pytest:

```bash
pip install -r app/requirements.txt
python -m pytest tests/ -v
```

## 📊 Monitoring

The application exposes Prometheus metrics at `/metrics` endpoint:

- `download_requests_total` - Download request counter
- `download_duration_seconds` - Download duration histogram
- `health_check_requests_total` - Health check counter

## 📁 Project Structure

```
.
├── app/                    # Application source code
│   ├── main.py            # Flask application
│   └── requirements.txt   # Python dependencies
├── docs/                  # Documentation
│   ├── ci-cd-setup-guide.md # CI/CD setup instructions
│   ├── monitoring-logging.md # Monitoring and logging strategy
│   └── test-plan.md       # Test plan and validation procedures
├── k8s/                   # Kubernetes manifests
│   ├── deploy.yaml
│   ├── hpa.yaml
│   ├── namespace.yaml
│   ├── rbac.yaml
│   └── service.yaml
├── scripts/               # Deployment scripts
│   └── k8s-deploy.sh
├── tests/                 # Unit tests
│   └── test_basic.py
├── Dockerfile             # Docker configuration
├── Jenkinsfile            # CI/CD pipeline definition
├── kubeconfig-jenkins.yaml# Kubernetes configuration for Jenkins
├── REAL_CLUSTER_SETUP.md  # Instructions for real cluster setup
└── README.md              # This file
```

## 📚 Documentation

Detailed documentation is available in the [docs](docs/) directory:

- [CI/CD Setup Guide](docs/ci-cd-setup-guide.md) - Complete setup instructions
- [Test Plan](docs/test-plan.md) - Validation procedures
- [Monitoring & Logging](docs/monitoring-logging.md) - Observability strategy
