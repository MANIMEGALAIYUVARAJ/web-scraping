pipeline {

    agent any

    environment {
        COMPOSE_PROJECT_NAME = "scrapper"

        VM_USER    = "ubuntu"
        VM_HOST    = "3.110.215.102"
        VM_APP_DIR = "/home/ubuntu/scrapper"

        FRONTEND_PORT = "3000"
        BACKEND_PORT  = "61631"
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo '🔄 Checking out code...'
                checkout scm
            }
        }

        stage('Copy Code to VM') {
            steps {
                sshagent(['aws-email-vm-ssh']) {
                    sh """
                    rsync -avz --delete \
                      --exclude=node_modules \
                      --exclude=.git \
                      --exclude=__pycache__ \
                      --exclude=.venv \
                      --no-perms \
                      --no-owner \
                      --no-group \
                      ./ ${VM_USER}@${VM_HOST}:${VM_APP_DIR}/ || true
                    """
                }
            }
        }

        stage('Deploy on VM') {
            steps {
                sshagent(['aws-email-vm-ssh']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} '
                        set -e
                        cd ${VM_APP_DIR}

                        echo "📁 Verifying files"
                        ls -l

                        echo "🛑 Stopping containers"
                        docker compose down || true

                        echo "🏗️ Building images"
                        docker compose build

                        echo "🚀 Starting containers"
                        docker compose up -d

                        echo "📦 Running containers"
                        docker ps
                    '
                    """
                }
            }
        }

        stage('Test Deployment') {
            steps {
                sshagent(['aws-email-vm-ssh']) {
                    sh """
                    echo "⏳ Waiting for services to stabilize..."
                    sleep 60

                    ssh -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST} '
                        echo "🔍 Caddy / Frontend check (HTTP)"
                        curl --fail https://scrapper.cubegtp.com || exit 1

                      
                    '
                    """
                }
            }
        }
    }

    post {
        success {
            echo '🎉 scrapper deployed successfully on VM!'
        }
        failure {
            echo '❌ Deployment failed. Check Jenkins logs.'
        }
        always {
            cleanWs()
        }
    }
}
