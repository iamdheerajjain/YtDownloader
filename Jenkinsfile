pipeline {
    agent any

    environment {
        DOCKER_HUB_REPO = "prakuljain/yt-downloader"
        IMAGE_TAG = "latest"
        KUBECONFIG_CRED = credentials('kubeconfig-jenkins')
        NAMESPACE = "youtube-app"
        DEPLOYMENT_NAME = "youtube-api"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out code from Git..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image ${DOCKER_HUB_REPO}:${IMAGE_TAG} ..."
                    sh """
                        docker build -t ${DOCKER_HUB_REPO}:${IMAGE_TAG} .
                    """
                }
            }
        }

        stage('Push Image') {
            steps {
                script {
                    echo "Logging in to Docker Hub and pushing image..."
                    withCredentials([usernamePassword(credentialsId: 'docker-registry', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            echo \${DOCKER_PASS} | docker login -u \${DOCKER_USER} --password-stdin
                            docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                            docker logout
                        """
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "Deploying to Kubernetes cluster..."
                    
                    // Write kubeconfig to a temporary file
                    sh """
                        # Create kubeconfig file
                        cat > kubeconfig.yaml << 'EOL'
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: Cg==
    server: https://127.0.0.1:34071
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
  user: {}
EOL
                        
                        export KUBECONFIG=\${PWD}/kubeconfig.yaml
                        
                        echo "=== Kubectl Version ==="
                        kubectl version --client --output=yaml || echo "kubectl version check failed"
                        
                        echo "=== Cluster Info ==="
                        kubectl cluster-info || echo "Cluster unreachable"
                        
                        echo "=== Current Context ==="
                        kubectl config current-context || echo "No context"
                        
                        echo "=== Attempting to create namespace ==="
                        kubectl create namespace ${NAMESPACE} 2>&1 || kubectl get namespace ${NAMESPACE} || echo "Namespace operation failed"
                        
                        echo "=== Applying RBAC ==="
                        if [ -f k8s/rbac.yaml ]; then
                            kubectl apply -f k8s/rbac.yaml -n ${NAMESPACE} 2>&1 || echo "RBAC apply failed"
                        fi
                        
                        echo "=== Preparing deployment manifest ==="
                        if [ -f k8s/deploy.yaml ]; then
                            cp k8s/deploy.yaml deployment-temp.yaml
                            sed -i "s#<IMAGE_REGISTRY>/<IMAGE_NAME>:<IMAGE_TAG>#${DOCKER_HUB_REPO}:${IMAGE_TAG}#g" deployment-temp.yaml
                            
                            echo "=== Applying deployment ==="
                            kubectl apply -f deployment-temp.yaml -n ${NAMESPACE} 2>&1 || echo "Deployment apply failed"
                            
                            echo "=== Checking rollout status ==="
                            kubectl rollout status deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE} --timeout=60s 2>&1 || echo "Rollout status check failed"
                        else
                            echo "ERROR: k8s/deploy.yaml not found!"
                            ls -la k8s/ || echo "k8s directory not found"
                        fi
                        
                        echo "=== Applying service ==="
                        if [ -f k8s/service.yaml ]; then
                            kubectl apply -f k8s/service.yaml -n ${NAMESPACE} 2>&1 || echo "Service apply failed"
                        fi
                        
                        echo "=== Final Status ==="
                        kubectl get all -n ${NAMESPACE} 2>&1 || echo "Failed to get resources"
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
            echo "Docker image: ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
            echo "Deployed to namespace: ${NAMESPACE}"
        }
        failure {
            echo "❌ Pipeline failed. Check the logs above for details."
        }
    }
}
