pipeline {
    agent any

    environment {
        // היוזר שלך בדוקר האב
        DOCKERHUB_USER = "nafrin" 
        
        RELEASE_NAME = "my-calendar"
        CHART_DIR = "./calendar-chart"
        KUBECONFIG = "C:\\Users\\MyPc\\.kube\\config"
        HELM_CMD = "C:\\Helm\\helm.exe"
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
                    echo "🛠️ Building Images locally..."
                    bat 'docker build -t calendar-api:latest ./calendar_api'
                    bat 'docker build -t calendar-front:latest ./calendar_front'
                    bat 'docker build -t dashboard:latest ./dashboard'
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    echo "🧪 Running PyTest inside the Calendar API container..."
                    // הרצת הטסט מתוך קונטיינר זמני כדי לוודא שהקוד תקין
                    bat 'docker run --rm calendar-api:latest python -m pytest test_api.py -v'
                    echo "✅ Tests passed! The code is safe for deployment."
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    echo "🔒 Logging into Docker Hub..."
                    // שימוש ב-ID המדויק שיצרת בג'נקינס
                    withCredentials([usernamePassword(credentialsId: 'docker_hub_user', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                        // התחברות לדוקר
                        bat 'docker login -u %DOCKER_USER% -p %DOCKER_PASS%'
                        
                        echo "🏷️ Tagging images..."
                        bat "docker tag calendar-api:latest ${DOCKERHUB_USER}/calendar-api:latest"
                        bat "docker tag calendar-front:latest ${DOCKERHUB_USER}/calendar-front:latest"
                        bat "docker tag dashboard:latest ${DOCKERHUB_USER}/dashboard:latest"

                        echo "☁️ Pushing images to Docker Hub..."
                        bat "docker push ${DOCKERHUB_USER}/calendar-api:latest"
                        bat "docker push ${DOCKERHUB_USER}/calendar-front:latest"
                        bat "docker push ${DOCKERHUB_USER}/dashboard:latest"
                    }
                }
            }
        }

        stage('Deploy to K8s (Helm)') {
            steps {
                script {
                    echo "🚀 Deploying with Helm..."
                    bat "\"${HELM_CMD}\" upgrade --install ${RELEASE_NAME} ${CHART_DIR}"
                }
            }
        }

        stage('Apply Updates (Rollout)') {
            steps {
                script {
                    echo "🔄 Restarting pods to pull the NEW images from Docker Hub..."
                    withEnv(["KUBECONFIG=${env.KUBECONFIG}"]) {
                        bat 'kubectl rollout restart deployment calendar-api'
                        bat 'kubectl rollout restart deployment calendar-front'
                        bat 'kubectl rollout restart deployment dashboard'
                    }
                }
            }
        }
    }

    post {
        success {
            echo "🎉 SUCCESS! Tested, pushed to Docker Hub, and deployed to Kubernetes."
        }
        failure {
            echo "❌ FAILED! The pipeline stopped. If tests failed, the buggy code was NOT deployed."
        }
    }
}
