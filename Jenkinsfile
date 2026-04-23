pipeline {
    agent any

    // ─────────────────────────────────────────
    // Variables globales du pipeline
    // ─────────────────────────────────────────
    environment {
        IMAGE_NAME    = "devops-taskmanager"
        DOCKER_USER   = "alphonsine"                         // ← changez ici
        IMAGE_TAG     = "v${BUILD_NUMBER}"
        CONTAINER_NAME = "taskmanager-test"
        APP_PORT      = "80"
        CONTAINER_PORT = "5000"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        // ─────────────────────────────────────
        // STAGE 1 — Checkout du code
        // ─────────────────────────────────────
        stage('📥 Checkout') {
            steps {
                echo "══════════════════════════════════════"
                echo " Checkout : ${env.GIT_BRANCH ?: 'local'}"
                echo "══════════════════════════════════════"
                checkout scm
            }
        }

        // ─────────────────────────────────────
        // STAGE 2 — Tests unitaires
        // ─────────────────────────────────────
        stage('🧪 Unit Tests') {
            steps {
                echo "══════════════════════════════════════"
                echo " Lancement des tests unitaires"
                echo "══════════════════════════════════════"
                sh '''
                    pip install --quiet flask pytest pytest-flask requests
                    pytest tests/ -v --tb=short
                '''
            }
        }

        // ─────────────────────────────────────
        // STAGE 3 — Build de l'image Docker
        // ─────────────────────────────────────
        stage('🔨 Build Docker Image') {
            steps {
                echo "══════════════════════════════════════"
                echo " Build : ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
                echo "══════════════════════════════════════"
                sh '''
                    docker build \
                        --build-arg APP_VERSION=${IMAGE_TAG} \
                        -t ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${DOCKER_USER}/${IMAGE_NAME}:latest \
                        .
                '''
            }
        }

        // ─────────────────────────────────────
        // STAGE 4 — Tests d'acceptance
        // ─────────────────────────────────────
        stage('✅ Acceptance Tests') {
            steps {
                echo "══════════════════════════════════════"
                echo " Démarrage du container de test"
                echo "══════════════════════════════════════"
                sh '''
                    # Nettoyage préventif
                    docker rm -f ${CONTAINER_NAME} || true

                    # Lancement du container
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:${CONTAINER_PORT} \
                        -e PORT=${CONTAINER_PORT} \
                        -e APP_VERSION=${IMAGE_TAG} \
                        ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}

                    # Attendre que l'app soit prête
                    echo "Waiting for app to start..."
                    sleep 5

                    # Vérifier que le container tourne
                    if ! docker ps | grep -q ${CONTAINER_NAME}; then
                        echo "ERROR: Container failed to start!"
                        docker logs ${CONTAINER_NAME}
                        exit 1
                    fi

                    # Test de l'endpoint principal
                    echo ">> Testing GET /"
                    curl -f http://172.17.0.1:${APP_PORT}/ || exit 1

                    # Test du healthcheck
                    echo ">> Testing GET /health"
                    curl -f http://172.17.0.1:${APP_PORT}/health | grep -q "healthy" || exit 1

                    # Test de l'API
                    echo ">> Testing GET /api/tasks"
                    curl -f http://172.17.0.1:${APP_PORT}/api/tasks | grep -q "tasks" || exit 1

                    echo "✅ All acceptance tests passed!"
                '''
            }
            post {
                always {
                    // Nettoyage du container de test
                    sh 'docker rm -f ${CONTAINER_NAME} || true'
                }
            }
        }

        // ─────────────────────────────────────
        // STAGE 5 — Push vers Docker Hub
        // ─────────────────────────────────────
        stage('🚀 Push to Docker Hub') {
            steps {
                echo "══════════════════════════════════════"
                echo " Push de l'image sur Docker Hub"
                echo "══════════════════════════════════════"
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
                        docker push ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${DOCKER_USER}/${IMAGE_NAME}:latest
                        docker logout
                    '''
                }
            }
        }

        // ─────────────────────────────────────
        // STAGE 6 — Déploiement en production
        // ─────────────────────────────────────
        stage('🌍 Deploy to Production') {
            steps {
                echo "══════════════════════════════════════"
                echo " Déploiement en production"
                echo "══════════════════════════════════════"
                sh '''
                    # Arrêt de l'ancienne version
                    docker rm -f ${IMAGE_NAME}-prod || true

                    # Lancement de la nouvelle version
                    docker run -d \
                        --name ${IMAGE_NAME}-prod \
                        --restart always \
                        -p 80:${CONTAINER_PORT} \
                        -e PORT=${CONTAINER_PORT} \
                        -e APP_VERSION=${IMAGE_TAG} \
                        ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}

                    sleep 3

                    # Vérification finale
                    curl -f http://172.17.0.1/health | grep -q "healthy"
                    echo "✅ Deployed successfully: ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
                '''
            }
        }
    }

    // ─────────────────────────────────────────
    // Notifications post-pipeline
    // ─────────────────────────────────────────
    post {
        success {
            echo """
            ╔══════════════════════════════════════╗
            ║  ✅ PIPELINE SUCCEEDED                ║
            ║  Image : ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}
            ╚══════════════════════════════════════╝
            """
        }
        failure {
            echo """
            ╔══════════════════════════════════════╗
            ║  ❌ PIPELINE FAILED                   ║
            ║  Build : #${BUILD_NUMBER}              ║
            ╚══════════════════════════════════════╝
            """
            // Nettoyage en cas d'échec
            sh 'docker rm -f ${CONTAINER_NAME} || true'
        }
        always {
            // Nettoyage des images inutilisées
            sh 'docker image prune -f || true'
        }
    }
}
