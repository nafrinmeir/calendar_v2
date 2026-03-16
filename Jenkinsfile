pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "nafrin" 
        RELEASE_NAME = "my-calendar"
        CHART_DIR = "./calendar-chart"
        KUBECONFIG = "C:\\Users\\MyPc\\.kube\\config"
        HELM_CMD = "C:\\Helm\\helm.exe"
        IMAGE_TAG = "v${env.BUILD_ID}"
        
        // --- הגדרות GCP החדשות ---
        // מפנה את ג'נקינס לתיקיית ההתחברות של המשתמש שלך (ודא ש-MyPc זה שם המשתמש הנכון)
        CLOUDSDK_CONFIG = "C:\\Users\\MyPc\\AppData\\Roaming\\gcloud"
        GCP_PROJECT = "dgt-gcp-moe-it-labs-gke"
        GKE_CLUSTER = "test-gke-cluster"
        GKE_REGION = "me-west1"
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
                        
                        echo "🏷️ Tagging and Pushing images to Docker Hub..."
                        bat "docker tag calendar-api:${IMAGE_TAG} ${DOCKERHUB_USER}/calendar-api:${IMAGE_TAG}"
                        bat "docker tag calendar-front:${IMAGE_TAG} ${DOCKERHUB_USER}/calendar-front:${IMAGE_TAG}"
                        bat "docker tag dashboard:${IMAGE_TAG} ${DOCKERHUB_USER}/dashboard:${IMAGE_TAG}"

                        bat "docker push ${DOCKERHUB_USER}/calendar-api:${IMAGE_TAG}"
                        bat "docker push ${DOCKERHUB_USER}/calendar-front:${IMAGE_TAG}"
                        bat "docker push ${DOCKERHUB_USER}/dashboard:${IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Deploy to GCP (GKE)') {
            steps {
                script {
                    echo "🌍 Connecting to Google Kubernetes Engine..."
                    // שימוש במשתני הסביבה של KUBECONFIG ו-CLOUDSDK_CONFIG כדי לזייף את סביבת המשתמש שלך
                    withEnv(["KUBECONFIG=${env.KUBECONFIG}", "CLOUDSDK_CONFIG=${env.CLOUDSDK_CONFIG}"]) {
                        
                        // פקודת ההתחברות לקלסטר שהבאת לי
                        bat "gcloud container clusters get-credentials ${GKE_CLUSTER} --region ${GKE_REGION} --project ${GCP_PROJECT} --dns-endpoint"

                        echo "🚀 Deploying with Helm to the cloud..."
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

    post {
        success {
            echo "==================================================="
            echo "🎉 SUCCESS! The system was deployed to GOOGLE CLOUD!"
            echo "🔖 Deployed Version: ${IMAGE_TAG}"
            echo ""
            echo "⚠️  NOTE: You are now on a real cloud cluster."
            echo "Run 'kubectl get svc' in your terminal to find your REAL Public IPs!"
            echo "==================================================="
        }
        failure {
            echo "❌ FAILED! Pipeline stopped."
        }
    }
}
