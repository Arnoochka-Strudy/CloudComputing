# Домашняя работа по CI/CD

## В данной работе использовался Jenkins из-за проблем с Gitlab-CI/CD

### 1.Запуск docker с Jenkins

```bash
docker compose up -d --build 
```
### 2.Переходим в Jenkins и скачиваем следующие инструменты

 * Pipeline
 * Git
 * Email Extension
 * Docker
 * DOcker Pipeline

### 3.Коммитим репозиторий на Github или Gitlab

### 4.В Jenkins добавляем Pipeline 

#### 4.1. Добавляем сссылку на Github

#### 4.2. Добавляем ветку, на которой будет работать Pipeline

### 4.2. Добавляем путь до Jenkinsfile

![add-git](./add-git.png)

### 5. Запускаем Pipeline в Jenkins

![result](./result.png)

**Дополнительно:** Логи работы Pipeline представлены в `jenkins.log`
