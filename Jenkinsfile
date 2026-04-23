pipeline {
    agent any

    environment {
        IMAGE_NAME     = "devops-taskmanager"
        DOCKER_USER    = "alphonsine"
        IMAGE_TAG      = "v${BUILD_NUMBER}"

        STAGING_HOST   = "IP_STAGING"
        PROD_HOST      = "IP_PROD"

        CONTAINER_PORT = "5000"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        stage('📥 Checkout') {
            steps {
                checkout scm
            }
        }

        stage('🧪 Unit Tests') {
            steps {
                sh '''
                    pip install -r webapp/requirements.txt
                    pip install pytest pytest-flask requests
                    pytest tests/ -v
                '''
            }
        }

        stage('🔨 Build Docker Image') {
            steps {
                sh '''
                    docker build \
                        -t ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${DOCKER_USER}/${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('🚀 Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                        docker push ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${DOCKER_USER}/${IMAGE_NAME}:latest
                        docker logout
                    '''
                }
            }
        }

        // 🔹 STAGING AUTO
        stage('🧪 Deploy to Staging') {
            steps {
                sshagent(['staging-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@${STAGING_HOST} << EOF

                        docker pull ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}

                        docker rm -f ${IMAGE_NAME}-staging || true

                        docker run -d \
                            --name ${IMAGE_NAME}-staging \
                            -p 8080:${CONTAINER_PORT} \
                            ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}

                        echo "Waiting for app..."
                        until curl -s http://localhost:8080/health; do sleep 2; done

                        echo "Staging OK"

                        EOF
                    '''
                }
            }
        }

        // 🔹 VALIDATION HUMAINE
        stage('🛑 Approval') {
            steps {
                input message: "Deploy to PRODUCTION?", ok: "Deploy"
            }
        }

        // 🔹 PROD
        stage('🌍 Deploy to Production') {
            steps {
                sshagent(['prod-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@${PROD_HOST} << EOF

                        docker pull ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}

                        docker rm -f ${IMAGE_NAME}-backup || true
                        docker rename ${IMAGE_NAME}-prod ${IMAGE_NAME}-backup || true

                        docker run -d \
                            --name ${IMAGE_NAME}-prod \
                            --restart always \
                            -p 80:${CONTAINER_PORT} \
                            ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}

                        sleep 5

                        if ! curl -f http://localhost/health; then
                            echo "Deploy failed, rollback..."
                            docker rm -f ${IMAGE_NAME}-prod
                            docker rename ${IMAGE_NAME}-backup ${IMAGE_NAME}-prod
                            docker start ${IMAGE_NAME}-prod
                            exit 1
                        fi

                        docker rm -f ${IMAGE_NAME}-backup || true

                        echo "Production OK"

                        EOF
                    '''
                }
            }
        }
    }
}