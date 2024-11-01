# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем зависимости и необходимые инструменты
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install ./google-chrome-stable_current_amd64.deb -y \
    && wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE | xargs -I {} wget https://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы проекта
WORKDIR /app
COPY . /app

# Устанавливаем зависимости Python
RUN pip install -r requirements.txt

# Запуск вашего приложения
CMD ["python", "main.py"]
