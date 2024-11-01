import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
import shutil
import asyncio
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка Telegram бота
TELEGRAM_TOKEN = "7771782869:AAExPxsTVITqzMHRQ3Z-I3PyHLpl4nKpG-c"
CHAT_ID = "YOUR_CHAT_ID"
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Настройка Selenium WebDriver
chrome_path = shutil.which("google-chrome")

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Запуск в безголовом режиме
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.binary_location = chrome_path

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Глобальные переменные для хранения ссылок и текста сообщений
forum_url = ""
message_text = ""

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Команда /start получена")
    await update.message.reply_text('Привет! Отправь мне ссылку на тему форума, а затем текст сообщения для публикации.')

# Обработчик ссылок на темы
async def handle_url(update: Update, context: CallbackContext) -> None:
    global forum_url
    forum_url = update.message.text
    logger.info(f"Ссылка на тему получена: {forum_url}")
    await update.message.reply_text('Ссылка на тему получена. Теперь отправь текст сообщения для публикации.')

# Обработчик текста сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    global message_text
    message_text = update.message.text
    logger.info(f"Текст сообщения получен: {message_text}")
    await update.message.reply_text('Сообщение получено. Начинаю постинг...')
    await post_message(update)

# Функция для постинга сообщения
async def post_message(update: Update) -> None:
    try:
        logger.info("Начинаю авторизацию на форуме")
        # Переход на страницу входа
        driver.get("https://rutor.amsterdam/login/")
        time.sleep(2)

        # Вводим данные для входа
        username_field = driver.find_element(By.NAME, "login")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys("turkmyxa")
        password_field.send_keys("mailruadmin94")
        password_field.send_keys(Keys.RETURN)
        time.sleep(3)

        # Проверка на наличие капчи
        try:
            captcha_image = driver.find_element(By.XPATH, "//img[@class='captcha_image']")
            captcha_url = captcha_image.get_attribute("src")

            # Скачиваем капчу и отправляем в Telegram
            logger.info("Капча обнаружена, отправляю изображение пользователю")
            captcha_response = requests.get(captcha_url)
            with open("captcha.png", "wb") as file:
                file.write(captcha_response.content)
            await context.bot.send_photo(chat_id=CHAT_ID, photo=open("captcha.png", "rb"))

            # Ожидаем ввода капчи пользователем
            await update.message.reply_text('Введите капчу:')

        except Exception as e:
            logger.info("Капча не обнаружена, продолжаю постинг")
            # Если капчи нет, продолжаем постинг
            driver.get(forum_url)
            time.sleep(2)

            message_field = driver.find_element(By.NAME, "message")
            message_field.send_keys(message_text)
            message_field.send_keys(Keys.RETURN)

            await update.message.reply_text('Сообщение успешно опубликовано!')

    except Exception as e:
        logger.error(f"Произошла ошибка при постинге: {e}")
        await update.message.reply_text(f'Произошла ошибка: {e}')

# Обработчик капчи
async def handle_captcha(update: Update, context: CallbackContext) -> None:
    try:
        captcha_code = update.message.text
        logger.info(f"Код капчи получен: {captcha_code}")
        captcha_field = driver.find_element(By.NAME, "captcha")
        captcha_field.send_keys(captcha_code)
        captcha_field.send_keys(Keys.RETURN)
        time.sleep(3)

        # Переходим к постингу после капчи
        driver.get(forum_url)
        time.sleep(2)

        message_field = driver.find_element(By.NAME, "message")
        message_field.send_keys(message_text)
        message_field.send_keys(Keys.RETURN)

        await update.message.reply_text('Сообщение успешно опубликовано!')
    except Exception as e:
        logger.error(f"Произошла ошибка при вводе капчи: {e}")
        await update.message.reply_text(f'Произошла ошибка при вводе капчи: {e}')

# Регистрация команд и обработчиков
start_handler = CommandHandler('start', start)
url_handler = MessageHandler(filters.Entity('url'), handle_url)
message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
captcha_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_captcha)

application.add_handler(start_handler)
application.add_handler(url_handler)
application.add_handler(message_handler)
application.add_handler(captcha_handler)

# Запуск бота
logger.info("Запуск бота")
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    application.run_polling()
