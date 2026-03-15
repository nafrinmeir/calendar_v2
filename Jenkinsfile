pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "nafrin" 
        RELEASE_NAME = "my-calendar"
        CHART_DIR = "./calendar-chart"
        KUBECONFIG = "C:\\Users\\MyPc\\.kube\\config"
        HELM_CMD = "C:\\Helm\\helm.exe"
        IMAGE_TAG = "v${env.BUILD_ID}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                echo "✅ Code checked out from GitHub successfully!"
            }
        }

        stage('Build Local Images') {
            steps {
                script {
                    echo "🛠️ Building Images locally with dynamic tag: ${IMAGE_TAG}..."
                    bat "docker build -t calendar-api:${IMAGE_TAG} ./calendar_api"
                    bat "docker build -t calendar-front:${IMAGE_TAG} ./calendar_front"
                    bat "docker build -t dashboard:${IMAGE_TAG} ./dashboard"
                }
            }
        }

        stage('Test All Built Images (Pre-Push)') {
            steps {
                script {
                    echo "🚀 Starting temporary containers for ALL services..."
                    bat "docker run -d --name temp-api -e MONGO_URI=\"mongodb://127.0.0.1:27017/db?serverSelectionTimeoutMS=2000\" -p 5091:5001 calendar-api:${IMAGE_TAG}"
                    bat "docker run -d --name temp-front -p 5092:5002 calendar-front:${IMAGE_TAG}"
                    bat "docker run -d --name temp-dash -e FRONT_URL=\"http://127.0.0.1:5002/health\" -e API_URL=\"http://127.0.0.1:5001/health\" -p 5090:5000 dashboard:${IMAGE_TAG}"
                    
                    try {
                        echo "🧪 Running Tests..."
                        bat '''
                        docker run --rm -v "%WORKSPACE%:/app" -w /app python:3.9-slim sh -c "pip install pytest requests && pytest test_services.py -v -s"
                        '''
                        echo "✅ All 3 tests passed!"
                    } finally {
                        echo "🧹 Cleaning up..."
                        bat 'docker rm -f temp-api temp-front temp-dash'
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    echo "🔒 Logging into Docker Hub..."
                    withCredentials([usernamePassword(credentialsId: 'docker_hub_user', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                        bat 'docker login -u %DOCKER_USER% -p %DOCKER_PASS%'
                        
                        echo "🏷️ Tagging images with Docker Hub username and Build ID..."
                        bat "docker tag calendar-api:${IMAGE_TAG} ${DOCKERHUB_USER}/calendar-api:${IMAGE_TAG}"
                        bat "docker tag calendar-front:${IMAGE_TAG} ${DOCKERHUB_USER}/calendar-front:${IMAGE_TAG}"
                        bat "docker tag dashboard:${IMAGE_TAG} ${DOCKERHUB_USER}/dashboard:${IMAGE_TAG}"

                        echo "☁️ Pushing validated images to Docker Hub..."
                        bat "docker push ${DOCKERHUB_USER}/calendar-api:${IMAGE_TAG}"
                        bat "docker push ${DOCKERHUB_USER}/calendar-front:${IMAGE_TAG}"
                        bat "docker push ${DOCKERHUB_USER}/dashboard:${IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Deploy to K8s (Helm)') {
            steps {
                script {
                    echo "🚀 Deploying with Helm directly from Docker Hub..."
                    withEnv(["KUBECONFIG=${env.KUBECONFIG}"]) {
                        // הוספנו את השורה האחרונה שדוחפת את הגרסה פנימה!
                        bat """
                        \"${HELM_CMD}\" upgrade --install ${RELEASE_NAME} ${CHART_DIR} \
                        --set api.image=${DOCKERHUB_USER}/calendar-api:${IMAGE_TAG} \
                        --set front.image=${DOCKERHUB_USER}/calendar-front:${IMAGE_TAG} \
                        --set dashboard.image=${DOCKERHUB_USER}/dashboard:${IMAGE_TAG} \
                        --set appVersion=${IMAGE_TAG}
                        """
                    }
                }
            }
        }
    }

    // הלינקים שביקשת! מודפסים יפה בסיום המוצלח של הפייפליין
    post {
        success {
            echo "==================================================="
            echo "🎉 SUCCESS! The system was deployed successfully."
            echo "🔖 Deployed Version: ${IMAGE_TAG}"
            echo ""
            echo "🌐 ACCESS YOUR SYSTEM HERE:"
            echo "📊 Dashboard (Live Architecture): http://localhost:5010"
            echo "📅 Calendar Frontend (App):       http://localhost:5012"
            echo "==================================================="
        }
        failure {
            echo "❌ FAILED! Pipeline stopped. K8s remains on the previous stable version."
        }
    }
}
