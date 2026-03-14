pipeline {
    // מריץ את הפייפליין על השרת המקומי שלך שבדקנו
    agent any

    // משתני סביבה כדי שיהיה קל לשנות שמות בעתיד אם נצטרך
    environment {
        RELEASE_NAME = "my-calendar"
        CHART_DIR = "./calendar-chart"
    }

    stages {
        stage('Checkout Code') {
            steps {
                // ג'נקינס אוטומטית מושך את הקוד מהריפוזיטורי של GitHub
                // שבו מוגדר הפייפליין הזה
                checkout scm
                echo "✅ Code checked out from GitHub successfully!"
            }
        }

        stage('Build Docker Images') {
            steps {
                // בניית כל האימג'ים מהקוד המעודכן שירד מגיטהאב
                script {
                    echo "🛠️ Building Calendar API Image..."
                    bat 'docker build -t calendar-api:latest ./calendar_api'

                    echo "🛠️ Building Calendar Frontend Image..."
                    bat 'docker build -t calendar-front:latest ./calendar_front'

                    echo "🛠️ Building Dashboard Image..."
                    bat 'docker build -t dashboard:latest ./dashboard'
                }
            }
        }

        stage('Deploy to K8s (Helm)') {
            steps {
                script {
                    echo "🚀 Deploying with Helm..."
                    // --install אומר ל-Helm: "אם זה לא קיים תתקין, אם קיים - תשדרג"
                    bat "helm upgrade --install ${RELEASE_NAME} ${CHART_DIR}"
                }
            }
        }

        stage('Apply Updates (Rollout)') {
            steps {
                // מכיוון שאנחנו משתמשים בתגית "latest", קוברנטיס צריך "בעיטה"
                // כדי להבין שהוא צריך להשתמש באימג'ים החדשים שבנינו הרגע
                script {
                    echo "🔄 Restarting pods to pull the new images..."
                    bat 'kubectl rollout restart deployment calendar-api'
                    bat 'kubectl rollout restart deployment calendar-front'
                    bat 'kubectl rollout restart deployment dashboard'
                }
            }
        }
    }

    // בלוק פוסט לדיווח סטטוס בסיום
    post {
        success {
            echo "🎉 SUCCESS! The Calendar App was automatically built and deployed to Kubernetes."
        }
        failure {
            echo "❌ FAILED! Something went wrong in the pipeline. Check the logs above."
        }
    }
}
