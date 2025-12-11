pipeline {
    agent any
    
    environment {
        PYTHONUNBUFFERED = '1' 
        PROJECT_DIR = 'CI-CD'
    }
    
    stages {
        
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                dir("${PROJECT_DIR}") {
                    sh '''
                        echo "Настройка окружения..."
                        python3 --version
                        
                        if [ ! -d "venv" ]; then
                            python3 -m venv venv
                        fi
                    '''
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                dir("${PROJECT_DIR}") { 
                    sh '''
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                dir("${PROJECT_DIR}") { 
                    sh '''
                        . venv/bin/activate
                        echo "Запуск тестов..."
                        
                        mkdir -p reports
                        
                        python3 -m pytest tests/Test* --verbose --junitxml=reports/junit.xml
                    '''
                }
            }
            post {
                always {
                    junit "${PROJECT_DIR}/reports/junit.xml" 
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                dir("${PROJECT_DIR}") {
                    script {
                        echo "Сборка Docker образа..."
                        sh 'docker build -t scalar-pipeline:${BUILD_ID} .'
                        
                        sh '''
                            if docker images | grep -q "scalar-pipeline"; then
                                echo "Docker образ создан"
                            else
                                echo "Ошибка сборки Docker образа"
                                exit 1
                            fi
                        '''
                    }
                }
            }
        }
        
        stage('Test Docker Image') {
            steps {
                dir("${PROJECT_DIR}") {
                    echo "Тестируем Docker образ..."
                    sh '''
                        docker rm -f scalar-test || true
                        docker run -d --name scalar-test scalar-pipeline:${BUILD_ID}
                        EXIT_CODE=$(docker wait scalar-test)

                        echo "Логи контейнера:"
                        docker logs scalar-test

                        if [ "$EXIT_CODE" -eq 0 ]; then
                            echo "Docker образ успешно выполнил скрипт (Код $EXIT_CODE)"
                            docker rm -f scalar-test
                        else
                            echo "Docker образ завершился с ошибкой Python (Код $EXIT_CODE)"
                            docker rm -f scalar-test || true
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Push to Registry') {
            steps {
                dir("${PROJECT_DIR}") {
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-hub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        script {
                            def fullImageName = "arno4ka/scalar-pipeline:${BUILD_ID}"

                            sh "docker tag scalar-pipeline:${BUILD_ID} ${fullImageName}"

                            sh "echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin"

                            sh "docker push ${fullImageName}"

                            echo "Образ ${fullImageName} опубликован!"
                        }
                    }
                }
            }
        }
        
        stage('Deploy Notification') {
            steps {
                echo "CI/CD Pipeline завершен!"
            }
        }
    }
    
    post {
        always {
            echo 'Сборка завершена'
            sh 'docker system prune -f || true'
        }
    }
}