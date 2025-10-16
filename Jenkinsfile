stages {
    stage('Checkout') {
        steps {
            git branch: 'master',
                credentialsId: 'gonudayo',
                url: 'https://lab.ssafy.com/m13-ai-news/S13P21M703.git'
        }
    }

    stage('Setup Network & Database') {
        steps {
            echo '네트워크 및 DB 설정'
            sh '''
                docker network create app-network || true
                docker stop postgres-container || true
                docker rm postgres-container || true

                docker run -d \
                    --name postgres-container \
                    --network app-network \
                    -e POSTGRES_DB=ww \
                    -e POSTGRES_USER=postgres \
                    -e POSTGRES_PASSWORD=6363 \
                    -p 5432:5432 \
                    -v postgres_data:/var/lib/postgresql/data \
                    --restart=unless-stopped \
                    postgres:15-alpine

                sleep 10
            '''
        }
    }

    stage('Build Backend') {
        steps {
            dir('server') {
                sh 'docker build -t backend-app .'
            }
        }
    }

    stage('Deploy Backend') {
        steps {
            sh '''
                docker stop backend-container || true
                docker rm backend-container || true

                docker run -d \
                    --name backend-container \
                    --network app-network \
                    --env-file /var/lib/jenkins/workspace/frontend-pipeline/server/.env \
                    -p 9000:9000 \
                    backend-app:latest
            '''
        }
    }

    stage('Build & Deploy Frontend') {
        steps {
            dir('client') {
                sh '''
                    docker stop frontend-container || true
                    docker rm frontend-container || true
                    docker rmi frontend-app:latest || true

                    docker build -t frontend-app .
                    docker run -d \
                      --name frontend-container \
                      --network app-network \
                      -p 8081:80 \
                      frontend-app:latest
                '''
            }
        }
    }
}

post {
    success {
        mattermostSend(
            message: "✅ 배포 성공 : ${JOB_NAME} #${BUILD_NUMBER}",
            color: "good"
        )
    }
    failure {
        mattermostSend(
            message: "❌ 배포 실패 : ${JOB_NAME} #${BUILD_NUMBER}",
            color: "danger"
        )
    }
}