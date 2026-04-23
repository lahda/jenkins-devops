pipeline {
    agent any

    environment {
        IMAGE_NAME = "taskmanager-app"
        DOCKERHUB_CREDENTIALS = "dockerhub-credentials"
        DOCKERHUB_REPO = "alphonsine/taskmanager-app"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                echo "Building Docker image..."
                docker build -t $IMAGE_NAME:${BUILD_NUMBER} .
                """
            }
        }

        stage('Test Container') {
            steps {
                sh """
                echo "Cleaning old container..."
                docker rm -f test-app || true

                echo "Starting container..."
                docker run -d --name test-app -p 5001:5000 $IMAGE_NAME:${BUILD_NUMBER}

                echo "Waiting for app..."
                sleep 5

                echo "Testing health endpoint..."
                curl -f http://localhost:5001/health

                echo "Stopping container..."
                docker rm -f test-app
                """
            }
        }

        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: DOCKERHUB_CREDENTIALS,
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    sh """
                    echo $PASS | docker login -u $USER --password-stdin
                    """
                }
            }
        }

        stage('Push Image') {
            steps {
                sh """
                docker tag $IMAGE_NAME:${BUILD_NUMBER} $DOCKERHUB_REPO:${BUILD_NUMBER}
                docker tag $IMAGE_NAME:${BUILD_NUMBER} $DOCKERHUB_REPO:latest

                docker push $DOCKERHUB_REPO:${BUILD_NUMBER}
                docker push $DOCKERHUB_REPO:latest
                """
            }
        }
    }

    post {
        always {
            sh """
            echo "Cleaning system..."
            docker rm -f test-app || true
            docker system prune -f || true
            """
        }
    }
}