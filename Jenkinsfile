pipeline {
    agent none

    environment {
        DOCKERHUB_AUTH = credentials('dockerhub-creds')
        ID_DOCKER      = "${DOCKERHUB_AUTH_USR}"
        IMAGE_NAME     = "taskmanager-app"
        IMAGE_TAG      = "${BUILD_NUMBER}"
        TEST_PORT      = "5001"    // ← port de test séparé
    }

    stages {

        stage('Build Image') {
            agent any
            steps {
                sh 'docker build -t ${ID_DOCKER}/${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }

        stage('Run container') {
            agent any
            steps {
                sh '''
                    echo "Clean environment"
                    docker rm -f ${IMAGE_NAME} || echo "container does not exist"

                    # ✅ Port 5001 pour éviter le conflit avec la prod (port 80)
                    docker run --name ${IMAGE_NAME} -d \
                        -p ${TEST_PORT}:5000 \
                        -e PORT=5000 \
                        ${ID_DOCKER}/${IMAGE_NAME}:${IMAGE_TAG}
                    sleep 5
                '''
            }
        }

        stage('Test image') {
            agent any
            steps {
                sh '''
                    curl -f http://172.17.0.1:${TEST_PORT}/health | grep -q "healthy"
                    echo "Test passed!"
                '''
            }
        }

        stage('Clean container') {
            agent any
            steps {
                sh 'docker rm -f ${IMAGE_NAME} || true'
            }
        }

        stage('Push Image to DockerHub') {
            agent any
            steps {
                sh '''
                    echo $DOCKERHUB_AUTH_PSW | docker login \
                        -u $DOCKERHUB_AUTH_USR \
                        --password-stdin
                    docker push ${ID_DOCKER}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker tag ${ID_DOCKER}/${IMAGE_NAME}:${IMAGE_TAG} \
                               ${ID_DOCKER}/${IMAGE_NAME}:latest
                    docker push ${ID_DOCKER}/${IMAGE_NAME}:latest
                    docker logout
                '''
            }
        }

        stage('Deploy in staging') {
            agent any
            environment {
                STAGING_HOST = "172.31.24.9"
            }
            steps {
                sshagent(credentials: ['staging-ssh']) {
                    sh '''
                        command1="echo $DOCKERHUB_AUTH_PSW | docker login -u $DOCKERHUB_AUTH_USR --password-stdin"
                        command2="docker pull $ID_DOCKER/$IMAGE_NAME:$IMAGE_TAG"
                        command3="docker rm -f webapp || echo 'app does not exist'"
                        command4="docker run -d -p 80:5000 -e PORT=5000 --name webapp --restart always $ID_DOCKER/$IMAGE_NAME:$IMAGE_TAG"
                        command5="sleep 3 && docker ps | grep webapp"

                        ssh -o StrictHostKeyChecking=no ubuntu@${STAGING_HOST} \
                            "$command1 && $command2 && $command3 && $command4 && $command5"
                    '''
                }
            }
        }

        stage('Verify Staging') {
            agent any
            environment {
                STAGING_HOST = "172.31.22.38"
            }
            steps {
                sh '''
                    sleep 5
                    curl -f http://${STAGING_HOST}/health | grep -q "healthy"
                    echo "Staging is healthy!"
                '''
            }
        }

        stage('Approval for Production') {
            agent none
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    input message: 'Staging OK ? Déployer en PRODUCTION ?',
                          ok: 'Oui, déployer !'
                }
            }
        }

        stage('Deploy in prod') {
            agent any
            environment {
                PROD_HOST = "172.31.16.182"    // ← IP privée Prod
            }
            steps {
                sshagent(credentials: ['prod-ssh']) {
                    sh '''
                        command1="echo $DOCKERHUB_AUTH_PSW | docker login -u $DOCKERHUB_AUTH_USR --password-stdin"
                        command2="docker pull $ID_DOCKER/$IMAGE_NAME:$IMAGE_TAG"
                        command3="docker rm -f webapp || echo 'app does not exist'"
                        command4="docker run -d -p 80:5000 -e PORT=5000 --name webapp --restart always $ID_DOCKER/$IMAGE_NAME:$IMAGE_TAG"
                        command5="sleep 3 && docker ps | grep webapp"

                        ssh -o StrictHostKeyChecking=no ubuntu@${PROD_HOST} \
                            "$command1 && $command2 && $command3 && $command4 && $command5"
                    '''
                }
            }
        }

        stage('Verify Production') {
            agent any
            environment {
                PROD_HOST = "172.31.X.X"
            }
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
            node('built-in') {
                sh '''
                    docker rm -f ${IMAGE_NAME} || true
                    docker system prune -f || true
                '''
            }
        }
        success {
            node('built-in') {
                echo "✅ PIPELINE SUCCESS — ${ID_DOCKER}/${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }
        failure {
            node('built-in') {
                echo "❌ PIPELINE FAILED — Build #${BUILD_NUMBER}"
            }
        }
    }
}