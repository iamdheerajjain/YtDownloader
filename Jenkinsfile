pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        DOCKER_REGISTRY = sh(script: "echo ${params.DOCKER_REGISTRY_OVERRIDE ?: 'docker.io'}", returnStdout: true).trim()
        DOCKER_HUB_REPO = sh(script: "echo ${params.DOCKER_REPO_OVERRIDE ?: 'prakuljain/yt-downloader'}", returnStdout: true).trim()
        NAMESPACE_BASE = sh(script: "echo ${params.NAMESPACE_OVERRIDE ?: 'youtube-app'}", returnStdout: true).trim()
        DEPLOYMENT_NAME = sh(script: "echo ${params.DEPLOYMENT_OVERRIDE ?: 'youtube-api'}", returnStdout: true).trim()
        IMAGE_TAG = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        LATEST_TAG = "latest"
    }

    parameters {
        choice(
            name: 'DEPLOY_ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Select environment to deploy to'
        )
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run unit tests before deployment'
        )
        booleanParam(
            name: 'SKIP_DEPLOYMENT',
            defaultValue: false,
            description: 'Skip deployment stage (for testing only)'
        )
        string(
            name: 'DOCKER_REGISTRY_OVERRIDE',
            defaultValue: '',
            description: 'Override default Docker registry (e.g., registry.example.com)'
        )
        string(
            name: 'DOCKER_REPO_OVERRIDE',
            defaultValue: '',
            description: 'Override default Docker repository (e.g., yourname/your-app)'
        )
        string(
            name: 'NAMESPACE_OVERRIDE',
            defaultValue: '',
            description: 'Override default Kubernetes namespace base name'
        )
        string(
            name: 'DEPLOYMENT_OVERRIDE',
            defaultValue: '',
            description: 'Override default deployment name'
        )
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "Checking out code from Git repository..."
                    checkout scm
                    echo "Repository: ${env.GIT_URL}"
                    echo "Branch: ${env.GIT_BRANCH}"
                    echo "Commit: ${GIT_COMMIT}"
                }
            }
        }

        stage('Code Quality Checks') {
            steps {
                script {
                    echo "Running code quality checks..."
                    sh '''
                        # Install quality checking tools
                        pip3 install flake8 bandit
                        
                        # Add local bin to PATH
                        export PATH=$PATH:/var/lib/jenkins/.local/bin:$HOME/.local/bin
                        
                        # Run Python code style checking (allow to continue even with warnings)
                        echo "Running flake8 code style checks..."
                        flake8 app/ --max-line-length=100 --exclude=__pycache__,*.pyc || echo "flake8 found style issues (continuing pipeline)"
                        
                        # Run security scanning
                        echo "Running bandit security checks..."
                        bandit -r app/ -ll || echo "bandit completed security scan"
                    '''
                }
            }
        }

        stage('Run Unit Tests') {
            when {
                expression { return params.RUN_TESTS }
            }
            steps {
                script {
                    echo "Running unit tests..."
                    sh '''
                        # Create a virtual environment for testing
                        python3 -m venv test_env
                        source test_env/bin/activate
                        
                        # Install dependencies
                        pip install -r app/requirements.txt
                        
                        # Run tests
                        python -m pytest tests/ -v
                        
                        # Cleanup
                        deactivate
                    '''
                }
            }
            post {
                always {
                    echo "Cleaning up test environment..."
                    sh 'rm -rf test_env || true'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image ${DOCKER_HUB_REPO}:${IMAGE_TAG} ..."
                    sh """
                        # Add local bin to PATH for any tools that might be needed
                        export PATH=\$PATH:/var/lib/jenkins/.local/bin:\$HOME/.local/bin
                        
                        echo "Building image ${DOCKER_HUB_REPO}:${IMAGE_TAG}..."
                        docker build -t ${DOCKER_HUB_REPO}:${IMAGE_TAG} .
                        BUILD_STATUS=\$?
                        if [ \$BUILD_STATUS -ne 0 ]; then
                            echo "ERROR: Docker build failed with exit code \$BUILD_STATUS"
                            exit 1
                        fi
                        
                        echo "Tagging image as ${DOCKER_HUB_REPO}:${LATEST_TAG}..."
                        docker tag ${DOCKER_HUB_REPO}:${IMAGE_TAG} ${DOCKER_HUB_REPO}:${LATEST_TAG}
                        TAG_STATUS=\$?
                        if [ \$TAG_STATUS -ne 0 ]; then
                            echo "ERROR: Docker tag failed with exit code \$TAG_STATUS"
                            exit 1
                        fi
                        
                        echo "Docker build and tag completed successfully"
                    """
                }
            }
            post {
                success {
                    echo "Docker image built successfully"
                    sh "docker images ${DOCKER_HUB_REPO}"
                }
                failure {
                    echo "Docker image build failed"
                }
            }
        }

        stage('Security Scan') {
            parallel {
                stage('Docker Image Scan') {
                    steps {
                        script {
                            echo "Scanning Docker image for vulnerabilities..."
                            sh '''
                                # Use Trivy for container scanning if available
                                if command -v trivy &> /dev/null; then
                                    trivy image --exit-code 0 --severity HIGH,CRITICAL ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                                else
                                    echo "Trivy not available, skipping Docker image scan"
                                    echo "Install Trivy to enable container vulnerability scanning"
                                fi
                            '''
                        }
                    }
                }
                stage('Dependency Scan') {
                    steps {
                        script {
                            echo "Scanning dependencies for vulnerabilities..."
                            sh '''
                                # Install safety for dependency scanning
                                pip3 install safety pip-audit
                                
                                # Add local bin to PATH
                                export PATH=$PATH:/var/lib/jenkins/.local/bin:$HOME/.local/bin
                                
                                # Run safety check
                                echo "Running safety dependency check..."
                                safety scan -r app/requirements.txt
                                SAFETY_EXIT_CODE=$?
                                if [ $SAFETY_EXIT_CODE -ne 0 ]; then
                                    echo "Safety scan found vulnerabilities with exit code $SAFETY_EXIT_CODE"
                                    # Continue with pipeline even if vulnerabilities found
                                fi
                                echo "safety scan completed"
                                
                                # Run pip-audit
                                echo "Running pip-audit dependency check..."
                                pip-audit -r app/requirements.txt
                                PIP_AUDIT_EXIT_CODE=$?
                                if [ $PIP_AUDIT_EXIT_CODE -ne 0 ]; then
                                    echo "pip-audit found vulnerabilities with exit code $PIP_AUDIT_EXIT_CODE"
                                    # Continue with pipeline even if vulnerabilities found
                                fi
                                echo "pip-audit completed"
                            '''
                        }
                    }
                }
            }
        }

        stage('Push Image') {
            steps {
                script {
                    echo "Pushing image to Docker registry..."
                    withCredentials([usernamePassword(credentialsId: 'docker-registry', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            # Add local bin to PATH
                            export PATH=$PATH:/var/lib/jenkins/.local/bin:$HOME/.local/bin
                            
                            # Validate that credentials are not empty
                            if [ -z "$DOCKER_USER" ] || [ -z "$DOCKER_PASS" ]; then
                                echo "ERROR: Docker credentials are not properly configured"
                                echo "DOCKER_USER: ${DOCKER_USER}"
                                echo "DOCKER_PASS length: ${#DOCKER_PASS}"
                                exit 1
                            fi
                            
                            echo "Attempting to login to Docker Hub as user: $DOCKER_USER"
                            echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                            LOGIN_STATUS=$?
                            if [ $LOGIN_STATUS -ne 0 ]; then
                                echo "ERROR: Docker login failed with exit code $LOGIN_STATUS"
                                echo "Please check your Docker Hub credentials in Jenkins"
                                exit 1
                            fi
                            
                            echo "Verifying that image exists locally before pushing..."
                            docker images ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                            IMAGE_EXISTS=$?
                            if [ $IMAGE_EXISTS -ne 0 ]; then
                                echo "ERROR: Image ${DOCKER_HUB_REPO}:${IMAGE_TAG} not found locally"
                                echo "Available images:"
                                docker images | head -10
                                exit 1
                            fi
                            
                            echo "Pushing image ${DOCKER_HUB_REPO}:${IMAGE_TAG}..."
                            docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                            PUSH_STATUS=$?
                            if [ $PUSH_STATUS -ne 0 ]; then
                                echo "ERROR: Docker push failed with exit code $PUSH_STATUS"
                                echo "Listing local images:"
                                docker images | grep ${DOCKER_HUB_REPO} || echo "No matching images found"
                                exit 1
                            fi
                            
                            echo "Pushing image ${DOCKER_HUB_REPO}:${LATEST_TAG}..."
                            docker push ${DOCKER_HUB_REPO}:${LATEST_TAG}
                            PUSH_LATEST_STATUS=$?
                            if [ $PUSH_LATEST_STATUS -ne 0 ]; then
                                echo "ERROR: Docker push of latest tag failed with exit code $PUSH_LATEST_STATUS"
                                exit 1
                            fi
                            
                            docker logout
                            echo "Successfully pushed both tags to Docker Hub"
                        '''
                    }
                }
            }
            post {
                success {
                    echo "Docker images pushed successfully"
                }
                failure {
                    echo "Docker image push failed"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                expression { return !params.SKIP_DEPLOYMENT }
            }
            steps {
                script {
                    echo "Deploying to Kubernetes cluster..."

                    def targetNamespace = "${NAMESPACE_BASE}-${params.DEPLOY_ENVIRONMENT}"
                    if (params.DEPLOY_ENVIRONMENT == 'production') {
                        targetNamespace = NAMESPACE_BASE
                    }
                    
                    echo "Deploying to namespace: ${targetNamespace}"

                    sh '''
                        export KUBECONFIG=${PWD}/kubeconfig-jenkins.yaml
                        
                        echo "=== Kubectl Version ==="
                        kubectl version --client --output=yaml
                        KUBECTL_VERSION_STATUS=$?
                        if [ $KUBECTL_VERSION_STATUS -ne 0 ]; then
                            echo "WARNING: kubectl version check failed with exit code $KUBECTL_VERSION_STATUS"
                        fi
                        
                        echo "=== Cluster Info ==="
                        kubectl cluster-info
                        CLUSTER_INFO_STATUS=$?
                        if [ $CLUSTER_INFO_STATUS -ne 0 ]; then
                            echo "ERROR: Cannot reach cluster - kubectl cluster-info failed with exit code $CLUSTER_INFO_STATUS"
                            echo "Current KUBECONFIG: $KUBECONFIG"
                            echo "File exists: $(test -f $KUBECONFIG && echo "YES" || echo "NO")"
                            if [ -f "$KUBECONFIG" ]; then
                                echo "Kubeconfig contents:"
                                cat $KUBECONFIG
                            fi
                            exit 1
                        fi
                        
                        echo "=== Current Context ==="
                        kubectl config current-context
                        CONTEXT_STATUS=$?
                        if [ $CONTEXT_STATUS -ne 0 ]; then
                            echo "ERROR: No valid context found - kubectl config current-context failed with exit code $CONTEXT_STATUS"
                            exit 1
                        fi
                        
                        echo "=== Creating namespace ${targetNamespace} ==="
                        kubectl create namespace ${targetNamespace} 2>/dev/null || kubectl get namespace ${targetNamespace} >/dev/null
                        NAMESPACE_STATUS=$?
                        if [ $NAMESPACE_STATUS -ne 0 ]; then
                            echo "ERROR: Failed to create or verify namespace ${targetNamespace}"
                            exit 1
                        fi
                        
                        echo "=== Applying RBAC ==="
                        if [ -f k8s/rbac.yaml ]; then
                            # Update namespace in RBAC file
                            sed "s/youtube-app/${targetNamespace}/g" k8s/rbac.yaml > rbac-temp.yaml
                            kubectl apply -f rbac-temp.yaml
                            RBAC_STATUS=$?
                            if [ $RBAC_STATUS -ne 0 ]; then
                                echo "ERROR: RBAC apply failed with exit code $RBAC_STATUS"
                                exit 1
                            fi
                        else
                            echo "WARNING: k8s/rbac.yaml not found, skipping RBAC configuration"
                        fi
                        
                        echo "=== Preparing deployment manifest ==="
                        if [ -f k8s/deploy.yaml ]; then
                            # Update namespace and image in deployment file
                            sed "s/youtube-app/${targetNamespace}/g" k8s/deploy.yaml > deployment-temp.yaml
                            sed -i "s#prakuljain/yt-downloader:latest#${DOCKER_HUB_REPO}:${IMAGE_TAG}#g" deployment-temp.yaml
                            
                            echo "=== Applying deployment ==="
                            kubectl apply -f deployment-temp.yaml
                            DEPLOY_STATUS=$?
                            if [ $DEPLOY_STATUS -ne 0 ]; then
                                echo "ERROR: Deployment apply failed with exit code $DEPLOY_STATUS"
                                exit 1
                            fi
                            
                            echo "=== Checking rollout status ==="
                            kubectl rollout status deployment/${DEPLOYMENT_NAME} -n ${targetNamespace} --timeout=120s
                            ROLLOUT_STATUS=$?
                            if [ $ROLLOUT_STATUS -ne 0 ]; then
                                echo "ERROR: Rollout status check failed with exit code $ROLLOUT_STATUS"
                                kubectl get pods -n ${targetNamespace}
                                kubectl describe deployment/${DEPLOYMENT_NAME} -n ${targetNamespace}
                                exit 1
                            fi
                        else
                            echo "ERROR: k8s/deploy.yaml not found!"
                            ls -la k8s/ || echo "k8s directory not found"
                            exit 1
                        fi
                        
                        echo "=== Applying service ==="
                        if [ -f k8s/service.yaml ]; then
                            # Update namespace in service file
                            sed "s/youtube-app/${targetNamespace}/g" k8s/service.yaml > service-temp.yaml
                            kubectl apply -f service-temp.yaml
                            SERVICE_STATUS=$?
                            if [ $SERVICE_STATUS -ne 0 ]; then
                                echo "ERROR: Service apply failed with exit code $SERVICE_STATUS"
                                exit 1
                            fi
                        else
                            echo "WARNING: k8s/service.yaml not found, skipping service configuration"
                        fi
                        
                        echo "=== Applying HPA ==="
                        if [ -f k8s/hpa.yaml ]; then
                            # Update namespace in HPA file
                            sed "s/youtube-app/${targetNamespace}/g" k8s/hpa.yaml > hpa-temp.yaml
                            kubectl apply -f hpa-temp.yaml --validate=false
                            HPA_STATUS=$?
                            if [ $HPA_STATUS -ne 0 ]; then
                                echo "ERROR: HPA apply failed with exit code $HPA_STATUS"
                                exit 1
                            fi
                        else
                            echo "WARNING: k8s/hpa.yaml not found, skipping HPA configuration"
                        fi
                        
                        echo "=== Final Status ==="
                        kubectl get all -n ${targetNamespace}
                        echo "Deployment completed successfully"
                    '''
                }
            }
        }

        stage('Health Check') {
            when {
                expression { return !params.SKIP_DEPLOYMENT }
            }
            steps {
                script {
                    echo "Performing health checks..."
                    
                    def targetNamespace = "${NAMESPACE_BASE}-${params.DEPLOY_ENVIRONMENT}"
                    if (params.DEPLOY_ENVIRONMENT == 'production') {
                        targetNamespace = NAMESPACE_BASE
                    }
                    
                    sh """
                        export KUBECONFIG=\${PWD}/kubeconfig-jenkins.yaml
                        
                        # Check if pods are running
                        echo "=== Checking pod status ==="
                        kubectl get pods -n ${targetNamespace} -l app=youtube-api || echo "Failed to get pods"
                        
                        # Check service endpoints
                        echo "=== Checking service endpoints ==="
                        kubectl get endpoints youtube-api -n ${targetNamespace} || echo "No endpoints found"
                        
                        # Wait a bit for application to be ready
                        sleep 10
                        
                        # Try to access the application (if service is exposed)
                        echo "=== Checking application readiness ==="
                        kubectl get service youtube-api -n ${targetNamespace} -o wide || echo "Failed to get service info"
                    """
                }
            }
        }
    }

    post {
        success {
            script {
                echo "Pipeline completed successfully!"
                echo "Docker image: ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
                echo "Deployed to namespace: ${NAMESPACE_BASE}-${params.DEPLOY_ENVIRONMENT}"
                /*
                slackSend(
                    channel: '#jenkins',
                    message: "CI/CD Pipeline Successful!\\nRepository: ${env.GIT_URL}\\nBranch: ${env.GIT_BRANCH}\\nImage: ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
                )
                */
            }
        }
        failure {
            script {
                echo "Pipeline failed. Check the logs above for details."
                /*
                slackSend(
                    channel: '#jenkins',
                    message: "CI/CD Pipeline Failed!\\nRepository: ${env.GIT_URL}\\nBranch: ${env.GIT_BRANCH}\\nPlease check Jenkins for details."
                )
                */
            }
        }
        cleanup {
            script {
                echo "Cleaning up temporary files..."
                sh '''
                    rm -f kubeconfig-jenkins.yaml
                    rm -f deployment-temp.yaml rbac-temp.yaml service-temp.yaml hpa-temp.yaml || true
                '''
            }
        }
    }
}