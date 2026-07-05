pipeline {
    agent any

    environment {
                MONGO_URI = credentials('apgosar-mongo-uri')
                SECRET_KEY = credentials('apgosar-mongo-secret-key')
            }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh '''
                    echo "===== Build Stage ====="
                    echo "Creating .env file..."

                cat > .env <<EOF
MONGO_URI=$MONGO_URI
SECRET_KEY=$SECRET_KEY
EOF

                    python3 --version

                    echo "Contents of workspace:"
                    ls -la

                    python3 -m pip install --upgrade pip --break-system-packages

                    python3 -m pip install -r requirements.txt --break-system-packages
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    echo "===== Test Stage ====="

                    python3 -m pytest -v
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    echo "===== Deploy Stage ====="

                    # Remove old deployment folder if it exists
                    rm -rf deployment

                    # Create deployment directory
                    mkdir deployment

                    # Copy only required application files
                    cp app.py deployment/
                    cp requirements.txt deployment/
                    cp README.md deployment/
                    cp -r templates deployment/

                    echo "Deployment completed successfully."

                    echo "===== Deployment Files ====="
                    ls -R deployment
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
        }

        failure {
            echo "Pipeline failed!"
        }

        always {
            cleanWs()
        }
    }
}
