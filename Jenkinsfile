pipeline {
    agent any

    environment {
        IMAGE_NAME = "taskmanager-app"
        IMAGE_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = "test-app"
        PORT = "5001"
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
                    docker build -t $IMAGE_NAME:$IMAGE_TAG .
                """
            }
        }

stage('Test Container') {
    steps {
        sh '''
            echo "Cleaning old container..."
            docker rm -f test-app || true

            echo "Starting container..."
            docker run -d --name test-app -p 5001:5000 taskmanager-app:${BUILD_NUMBER}

            echo "Waiting for app startup..."
            sleep 10

            echo "Checking container status..."
            docker ps -a | grep test-app

            echo "Testing health endpoint..."
            for i in $(seq 1 10); do
                echo "Attempt $i"
                # ← 172.17.0.1 au lieu de localhost
                if curl -f http://172.17.0.1:5001/health; then
                    echo "✅ App is healthy!"
                    break
                fi
                if [ $i -eq 10 ]; then
                    echo "App failed to respond"
                    docker logs test-app
                    exit 1
                fi
                sleep 3
            done
        '''
    }
}
        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh """
                        echo $PASS | docker login -u $USER --password-stdin
                    """
                }
            }
        }

        stage('Push Image') {
            steps {
                sh """
                    docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:$IMAGE_TAG
                    docker push $IMAGE_NAME:$IMAGE_TAG
                """
            }
        }
    }

    post {
        always {
            sh """
                echo "Cleaning system..."
                docker rm -f $CONTAINER_NAME || true
                docker system prune -f || true
            """
        }
    }
}