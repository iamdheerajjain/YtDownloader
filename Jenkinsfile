pipeline {
    agent any

    environment {
        DOCKER_HUB_REPO = "prakuljain/yt-downloader"
        IMAGE_TAG = "latest"
        KUBECONFIG_CRED = credentials('kubeconfig-jenkins')
        GITHUB_TOKEN = credentials('github-token')
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
                        # Make the deployment script executable
                        chmod +x k8s-deploy.sh
                        
                        # Run the deployment script
                        ./k8s-deploy.sh ${KUBECONFIG_CRED} ${NAMESPACE} ${DEPLOYMENT_NAME} ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
            echo "Docker image: ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
            echo "Deployed to namespace: ${NAMESPACE}"
        }
        failure {
            echo "Pipeline failed. Check the logs above for details."
        }
        always {
            script {
                echo "Cleaning up workspace..."
                cleanWs()
            }
        }
    }
}
