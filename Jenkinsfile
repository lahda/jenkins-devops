pipeline {
    agent any

    environment {
        IMAGE_NAME     = "taskmanager-app"
        DOCKER_USER    = "alphonsine"
        BUILD_TAG      = "${BUILD_NUMBER}"
        CONTAINER_NAME = "test-app"
        HOST_IP        = "172.17.0.1"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image..."
                    docker build -t ${IMAGE_NAME}:${BUILD_TAG} .
                '''
            }
        }

        stage('Test Container') {
            steps {
                sh '''
                    echo "Cleaning old container..."
                    docker rm -f ${CONTAINER_NAME} || true

                    echo "Starting container..."
                    docker run -d --name ${CONTAINER_NAME} -p 5001:5000 ${IMAGE_NAME}:${BUILD_TAG}

                    echo "Waiting for app startup..."
                    sleep 10

                    echo "Checking container status..."
                    docker ps -a | grep ${CONTAINER_NAME}

                    echo "Testing health endpoint..."
                    for i in $(seq 1 10); do
                        echo "Attempt $i"
                        if curl -f http://${HOST_IP}:5001/health; then
                            echo "App is healthy!"
                            break
                        fi
                        if [ $i -eq 10 ]; then
                            echo "App failed to respond"
                            docker logs ${CONTAINER_NAME}
                            exit 1
                        fi
                        sleep 3
                    done
                '''
            }
        }

        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    sh '''
                        echo "$PASS" | docker login -u "$USER" --password-stdin
                    '''
                }
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    docker tag ${IMAGE_NAME}:${BUILD_TAG} ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}
                    docker tag ${IMAGE_NAME}:${BUILD_TAG} ${DOCKER_USER}/${IMAGE_NAME}:latest
                    docker push ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}
                    docker push ${DOCKER_USER}/${IMAGE_NAME}:latest
                    docker logout
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f ${IMAGE_NAME}-prod || true
                    docker run -d \
                        --name ${IMAGE_NAME}-prod \
                        --restart always \
                        -p 80:5000 \
                        -e PORT=5000 \
                        ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}
                    sleep 3
                    curl -f http://${HOST_IP}/health | grep -q "healthy"
                    echo "Deployed successfully: ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}"
                '''
            }
        }
    }

    post {
        always {
            sh '''
                echo "Cleaning system..."
                docker rm -f ${CONTAINER_NAME} || true
                docker system prune -f || true
            '''
        }
        success {
            echo "Pipeline SUCCESS - ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}"
        }
        failure {
            echo "Pipeline FAILED - Build #${BUILD_NUMBER}"
        }
    }
}