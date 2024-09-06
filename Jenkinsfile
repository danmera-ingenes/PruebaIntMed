pipeline {
    agent any

    environment {
        GIT_CREDENTIALS_ID = 'danmera-ingenes'
        GIT_PAT = credentials('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')
    }
    
    stages {

        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], 
                            userRemoteConfigs: [[url: 'https://github.com/danmera-ingenes/PruebaIntMed.git', 
                                        credentialsId: GIT_PAT]]])
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
