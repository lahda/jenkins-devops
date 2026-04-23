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
        echo "Cleaning old container..."
        docker rm -f test-app || true

        echo "Starting test container..."
        docker run -d --name test-app -p 5001:5000 alphonsine/taskmanager-app:4

        sleep 5

        echo "Testing health endpoint..."
        curl -f http://localhost:5001/health

        echo "Stopping test container..."
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