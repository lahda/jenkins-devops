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
                sh """
                    echo "Cleaning old container..."
                    docker rm -f $CONTAINER_NAME || true

                    echo "Starting container..."
                    docker run -d --name $CONTAINER_NAME -p $PORT:5000 $IMAGE_NAME:$IMAGE_TAG

                    echo "Waiting for app startup..."
                    sleep 10

                    echo "Checking container status..."
                    docker ps -a | grep $CONTAINER_NAME || true

                    echo "Testing health endpoint..."
                    for i in \$(seq 1 10); do
                        echo "Attempt \$i"
                        curl -f http://localhost:$PORT/health && exit 0
                        sleep 3
                    done

                    echo "App failed to respond"
                    docker logs $CONTAINER_NAME
                    exit 1
                """
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