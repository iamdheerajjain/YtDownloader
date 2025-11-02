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
   - API Root: http://localhost:8080/
   - Health Check: http://localhost:8080/health
   - Readiness Check: http://localhost:8080/ready
   - Metrics: http://localhost:8080/metrics

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

## 🐳 Docker Support

The application is containerized using a multi-stage Dockerfile:

```bash
# Build the image
docker build -t yt-downloader .

# Run the container
docker run -p 8080:8080 yt-downloader
```

## ☸️ Kubernetes Deployment

Kubernetes manifests are provided for deployment:

```bash
# Apply all manifests
kubectl apply -f k8s/

# Or use the deployment script
./scripts/k8s-deploy.sh kubeconfig.yaml youtube-app youtube-api prakuljain/yt-downloader:latest
```

### Components

- **Deployment** - Manages application pods
- **Service** - Exposes application internally
- **HPA** - Automatically scales based on CPU usage
- **RBAC** - Secure access controls
- **Namespace** - Isolated environment

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
│   ├── ci-cd-setup-guide.md
│   ├── monitoring-logging.md
│   └── test-plan.md
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
└── README.md              # This file
```

## 🔧 Configuration

Environment variables:

- `DEBUG` - Enable debug mode (default: False)
- `MAX_DOWNLOAD_SIZE` - Maximum download size in MB (default: 100)
- `DOWNLOAD_FOLDER` - Folder for downloads (default: downloads)
- `APP_VERSION` - Application version (default: 1.0.0)

## 📚 Documentation

Detailed documentation is available in the [docs](docs/) directory:

- [CI/CD Setup Guide](docs/ci-cd-setup-guide.md) - Complete setup instructions
- [Test Plan](docs/test-plan.md) - Validation procedures
- [Monitoring & Logging](docs/monitoring-logging.md) - Observability strategy

## 🔒 Security

Security features:

- Non-root user in Docker container
- Kubernetes RBAC for minimal permissions
- Security scanning in CI/CD pipeline
- Secure credential handling in Jenkins

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue on the GitHub repository.
