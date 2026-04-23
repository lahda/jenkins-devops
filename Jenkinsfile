pipeline {
    agent any

    environment {
        IMAGE_NAME = "taskmanager-app"
        IMAGE_TAG = "6"
        DOCKERHUB_CREDENTIALS = "dockerhub-credentials"
        DOCKERHUB_REPO = "alphonsine/taskmanager-app"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv || true
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r webapp/requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                . venv/bin/activate
                PYTHONPATH=. pytest tests/ -v || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t $DOCKERHUB_REPO:$IMAGE_TAG .
                docker tag $DOCKERHUB_REPO:$IMAGE_TAG $DOCKERHUB_REPO:latest
                '''
            }
        }

        stage('Test Container') {
            steps {
                sh '''
                echo "Cleaning old container..."
                docker rm -f test-app || true

                echo "Starting container..."
                docker run -d --name test-app -p 5001:5000 $DOCKERHUB_REPO:$IMAGE_TAG

                echo "Waiting for app..."
                sleep 8

                echo "Container logs:"
                docker logs test-app || true

                echo "Health check:"
                curl -f http://localhost:5001/health
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
                    echo "$PASS" | docker login -u "$USER" --password-stdin
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
            sh '''
            docker rm -f test-app || true
            docker system prune -f || true
            '''
        }
    }
}