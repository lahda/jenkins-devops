pipeline {
    agent any

    environment {
        IMAGE_NAME = "taskmanager-app"
        DOCKERHUB_REPO = "alphonsine/taskmanager-app"
        DOCKERHUB_CREDENTIALS = "dockerhub-credentials"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $DOCKERHUB_REPO:$IMAGE_TAG ."
                sh "docker tag $DOCKERHUB_REPO:$IMAGE_TAG $DOCKERHUB_REPO:latest"
            }
        }

        stage('Test Container') {
            steps {
                sh '''
                docker run -d --name test-app -p 5000:5000 $DOCKERHUB_REPO:$IMAGE_TAG
                sleep 5
                curl -f http://localhost:5000/health
                docker rm -f test-app
                '''
            }
        }

        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: DOCKERHUB_CREDENTIALS,
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    sh '''
                    echo $PASS | docker login -u $USER --password-stdin
                    '''
                }
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                docker push $DOCKERHUB_REPO:$IMAGE_TAG
                docker push $DOCKERHUB_REPO:latest
                '''
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f || true'
        }
    }
}