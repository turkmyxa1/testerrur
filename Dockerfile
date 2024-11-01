# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем Chrome и ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install ./google-chrome-stable_current_amd64.deb -y \
    && wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver

# Копируем файлы проекта
WORKDIR /app
COPY . /app

# Устанавливаем зависимости Python
RUN pip install -r requirements.txt

# Запуск вашего приложения
CMD ["python", "main.py"]