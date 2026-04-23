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

        stage('Install Dependencies') {
            steps {
                sh 'python -m venv venv'
                sh '. venv/bin/activate && pip install -r webapp/requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh '. venv/bin/activate && PYTHONPATH=. pytest tests/'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDENTIALS, usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh 'echo $PASS | docker login -u $USER --password-stdin'
                }
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                docker tag $IMAGE_NAME $DOCKERHUB_REPO:latest
                docker push $DOCKERHUB_REPO:latest
                '''
            }
        }
    }
}