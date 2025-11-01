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
                    sh """
                        export KUBECONFIG=${KUBECONFIG_CRED}
                        
                        # Create namespace if it doesn't exist
                        kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                        
                        # Apply RBAC
                        kubectl apply -f k8s/rbac.yaml -n ${NAMESPACE} || true
                        
                        # Check if deployment exists
                        if kubectl get deployment ${DEPLOYMENT_NAME} -n ${NAMESPACE} >/dev/null 2>&1; then
                            echo "Updating existing deployment..."
                            kubectl set image deployment/${DEPLOYMENT_NAME} ${DEPLOYMENT_NAME}=${DOCKER_HUB_REPO}:${IMAGE_TAG} -n ${NAMESPACE}
                        else
                            echo "Creating new deployment..."
                            sed "s#<IMAGE_REGISTRY>/<IMAGE_NAME>:<IMAGE_TAG>#${DOCKER_HUB_REPO}:${IMAGE_TAG}#g" k8s/deploy.yaml | kubectl apply -n ${NAMESPACE} -f -
                        fi
                        
                        # Wait for rollout to complete
                        kubectl rollout status deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE} --timeout=120s
                        
                        echo "Deployment successful!"
                        kubectl get pods -n ${NAMESPACE}
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
