#!/bin/bash

# Обновление пакетов
apt-get update

# Установка Python и необходимых утилит
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    software-properties-common \
    curl \
    git \
    wget

# Установка Docker CLI
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Создаем симлинк для python
ln -s /usr/bin/python3 /usr/bin/python

# Добавляем пользователя jenkins в группу docker
usermod -aG docker jenkins

# Проверяем установку
python3 --version
pip3 --version
docker --version
docker-compose --version