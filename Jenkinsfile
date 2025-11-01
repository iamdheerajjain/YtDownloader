pipeline {
    agent any

    environment {
        DOCKER_HUB_REPO = "prakuljain/yt-downloader"
        IMAGE_TAG = "latest"
        REG_USER = credentials('prakuljain')
        REG_PASS = credentials('divya123')
        KUBECONFIG = credentials('kubeconfig-jenkins.yaml')
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
                    echo "Logging in to Docker Hub..."
                    sh """
                        echo ${REG_PASS} | docker login -u ${REG_USER} --password-stdin
                        docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                        docker logout
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "Deploying to Kubernetes..."
                    writeFile file: 'kubeconfig.yaml', text: KUBECONFIG
                    sh '''
                        export KUBECONFIG=kubeconfig.yaml
                        kubectl set image deployment/yt-downloader yt-downloader=${DOCKER_HUB_REPO}:${IMAGE_TAG} --namespace=default || \
                        kubectl apply -f k8s/deployment.yaml
                        kubectl rollout status deployment/yt-downloader --namespace=default
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed"
        }
        always {
          script {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
    }
}
