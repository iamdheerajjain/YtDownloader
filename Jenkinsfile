pipeline {
  agent any

  environment {
    REGISTRY = "docker.i"
    IMAGE_NAMESPACE = "prakuljain"
    IMAGE_NAME = "youtube-downloader-api"
    K8S_NAMESPACE = "youtube-app"
    DEPLOYMENT_NAME = "youtube-api"

    DOCKER_CRED_ID = "docker-registry"
    KUBECONFIG_CRED_ID = "kubeconfig"
    }

  options {
    skipDefaultCheckout(true)
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '50'))
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Unit Tests') {
      steps {
        dir('app') {
          sh 'python -m pip install --upgrade pip'
          sh 'pip install -r requirements.txt'
          sh 'pytest -q || true'
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          IMAGE_TAG = "${env.BUILD_ID}-${env.GIT_COMMIT.take(7)}"
          IMAGE_FULL = "${REGISTRY}/${IMAGE_NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"
        }
        sh "docker build -t ${IMAGE_FULL} ."
      }
    }

    stage('Push Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: env.DOCKER_CRED_ID, usernameVariable: 'REG_USER', passwordVariable: 'REG_PASS')]) {
          sh '''
            echo "$REG_PASS" | docker login ${REGISTRY} -u "$REG_USER" --password-stdin
            docker push ${IMAGE_FULL}
            docker logout ${REGISTRY}
          '''
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        withCredentials([file(credentialsId: env.KUBECONFIG_CRED_ID, variable: 'KUBECONFIG_FILE')]) {
          sh '''
            export KUBECONFIG=${KUBECONFIG_FILE}
            kubectl --kubeconfig=${KUBECONFIG_FILE} create namespace ${K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
            kubectl --kubeconfig=${KUBECONFIG_FILE} -n ${K8S_NAMESPACE} apply -f k8s/rbac.yaml || true
            kubectl --kubeconfig=${KUBECONFIG_FILE} -n ${K8S_NAMESPACE} apply -f k8s/service.yaml || true
            if kubectl --kubeconfig=${KUBECONFIG_FILE} -n ${K8S_NAMESPACE} get deployment ${DEPLOYMENT_NAME} > /dev/null 2>&1; then
              kubectl --kubeconfig=${KUBECONFIG_FILE} -n ${K8S_NAMESPACE} set image deployment/${DEPLOYMENT_NAME} ${DEPLOYMENT_NAME}=${IMAGE_FULL} --record
            else
              sed "s#<IMAGE_REGISTRY>/<IMAGE_NAME>:<IMAGE_TAG>#${IMAGE_FULL}#g" k8s/deploy.yaml | kubectl --kubeconfig=${KUBECONFIG_FILE} -n ${K8S_NAMESPACE} apply -f -
            fi
            kubectl --kubeconfig=${KUBECONFIG_FILE} -n ${K8S_NAMESPACE} rollout status deployment/${DEPLOYMENT_NAME} --timeout=120s
          '''
        }
      }
    }
  }

  post {
    success {
      echo "Deployment successful: ${IMAGE_FULL}"
    }
    failure {
      echo "Pipeline failed"
    }
    always {
      cleanWs()
    }
  }
}
