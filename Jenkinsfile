pipeline {
    agent any

    environment {
        IMAGE_NAME     = "taskmanager-app"
        DOCKER_USER    = "alphonsine"
        BUILD_TAG      = "${BUILD_NUMBER}"
        CONTAINER_NAME = "test-app"
        HOST_IP        = "172.17.0.1"
        STAGING_HOST   = "172.31.22.38"
        PROD_HOST      = "172.31.31.248"      // ← remplacez par l'IP privée de votre Prod
        DEPLOY_USER    = "ubuntu"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 20, unit: 'MINUTES')
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
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 5001:5000 ${IMAGE_NAME}:${BUILD_TAG}
                    sleep 10
                    for i in $(seq 1 10); do
                        echo "Attempt $i"
                        if curl -f http://${HOST_IP}:5001/health; then
                            echo "App is healthy!"
                            break
                        fi
                        if [ $i -eq 10 ]; then
                            docker logs ${CONTAINER_NAME}
                            exit 1
                        fi
                        sleep 3
                    done
                '''
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    sh '''
                        echo "$PASS" | docker login -u "$USER" --password-stdin
                        docker tag ${IMAGE_NAME}:${BUILD_TAG} ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}
                        docker tag ${IMAGE_NAME}:${BUILD_TAG} ${DOCKER_USER}/${IMAGE_NAME}:latest
                        docker push ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}
                        docker push ${DOCKER_USER}/${IMAGE_NAME}:latest
                        docker logout
                    '''
                }
            }
        }

        // ─────────────────────────────────────
        // STAGING
        // ─────────────────────────────────────
        stage('Deploy to Staging') {
            steps {
                sshagent(credentials: ['staging-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${STAGING_HOST} "
                            docker pull ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}
                            docker rm -f ${IMAGE_NAME}-staging || true
                            docker run -d \
                                --name ${IMAGE_NAME}-staging \
                                --restart always \
                                -p 80:5000 \
                                -e PORT=5000 \
                                ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}
                            sleep 3
                            docker ps | grep ${IMAGE_NAME}-staging
                            echo 'Staging deployment OK'
                        "
                    '''
                }
            }
        }

        stage('Smoke Test Staging') {
            steps {
                sh '''
                    sleep 5
                    curl -f http://${STAGING_HOST}/health | grep -q "healthy"
                    echo "Staging is healthy!"
                '''
            }
        }

        // ─────────────────────────────────────
        // APPROBATION MANUELLE
        // ─────────────────────────────────────
        stage('Approval for Production') {
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    input message: 'Staging OK ? Déployer en PRODUCTION ?',
                          ok: 'Oui, déployer en prod !'
                }
            }
        }

        // ─────────────────────────────────────
        // PRODUCTION
        // ─────────────────────────────────────
        stage('Deploy to Production') {
            steps {
                sshagent(credentials: ['prod-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${PROD_HOST} "
                            docker pull ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}
                            docker rm -f ${IMAGE_NAME}-prod || true
                            docker run -d \
                                --name ${IMAGE_NAME}-prod \
                                --restart always \
                                -p 80:5000 \
                                -e PORT=5000 \
                                ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG}
                            sleep 3
                            docker ps | grep ${IMAGE_NAME}-prod
                            echo 'Production deployment OK'
                        "
                    '''
                }
            }
        }

        stage('Verify Production') {
            steps {
                sh '''
                    sleep 5
                    curl -f http://${PROD_HOST}/health | grep -q "healthy"
                    echo "Production is healthy!"
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f ${CONTAINER_NAME} || true
                docker system prune -f || true
            '''
        }
        success {
            echo "PIPELINE SUCCESS - ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_TAG} deployé en PROD"
        }
        failure {
            echo "PIPELINE FAILED - Build #${BUILD_NUMBER}"
        }
    }
}