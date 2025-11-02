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
                    
                    // Write kubeconfig to a file
                    writeFile file: 'kubeconfig.yaml', text: readFile(KUBECONFIG_CRED)
                    
                    sh """
                        export KUBECONFIG=\${WORKSPACE}/kubeconfig.yaml
                        
                        echo "Testing kubectl connection..."
                        kubectl version --client || true
                        
                        echo "Creating namespace..."
                        kubectl create namespace ${NAMESPACE} 2>/dev/null || echo "Namespace already exists"
                        
                        echo "Applying Kubernetes manifests..."
                        
                        # Apply RBAC
                        if [ -f k8s/rbac.yaml ]; then
                            kubectl apply -f k8s/rbac.yaml -n ${NAMESPACE} || true
                        fi
                        
                        # Update deployment image in the manifest
                        if [ -f k8s/deploy.yaml ]; then
                            sed "s#<IMAGE_REGISTRY>/<IMAGE_NAME>:<IMAGE_TAG>#${DOCKER_HUB_REPO}:${IMAGE_TAG}#g" k8s/deploy.yaml > deployment-updated.yaml
                            kubectl apply -f deployment-updated.yaml -n ${NAMESPACE}
                        else
                            echo "Warning: k8s/deploy.yaml not found"
                        fi
                        
                        # Apply service if exists
                        if [ -f k8s/service.yaml ]; then
                            kubectl apply -f k8s/service.yaml -n ${NAMESPACE} || true
                        fi
                        
                        echo "Waiting for deployment to be ready..."
                        kubectl rollout status deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE} --timeout=120s || true
                        
                        echo "Deployment complete! Current pods:"
                        kubectl get pods -n ${NAMESPACE} || true
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
