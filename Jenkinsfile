pipeline {
    agent any
    
    environment {
        GIT_CREDENTIALS_ID = 'GitDanToken'
    }

    stages {
        stage('Clone Repository') {
            steps {
                // Use Jenkins credentials to clone the GitHub repository
                git credentialsId: "${GIT_CREDENTIALS_ID}", url: 'https://github.com/danmera-ingenes/PruebaIntMed.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                // Install any necessary dependencies
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Run Python Script') {
            steps {
                // Run the Python script with the specified arguments
                sh 'python leerDrive.py --token ./token.json --key ./key.json'
            }
        }
    }
    
    post {
        always {
            // Archive the results or logs, if any
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
