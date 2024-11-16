import telebot
import os
from dotenv import load_dotenv
import cloudpickle
import bot_function
from database_using import close_connection

# импорт файла с моделью
with open('model.pkl', 'rb') as f:
    model_pipeline = cloudpickle.load(f)

# Загружаем переменные из .env файла
load_dotenv()
try:
    # Читаем токен из переменной окружения
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    print("Токен загружен")
except:
    print("Что-то пошло не так! Введите Токен бота:")
    bot = telebot.TeleBot(input()) # в TOKEN мы вводим токен созданного бота в Telegram


# Привязываем обработчики команд и сообщений к боту
@bot.message_handler(commands=['start'])
def start(message):
    bot_function.start_bot(bot, message)

@bot.message_handler(commands=['help'])
def help(message):
    bot_function.help_bot(bot, message)

@bot.message_handler(commands = ['mute'])
def mute(bot,message):
    bot_function.mute_user(bot, message)

@bot.message_handler(commands = ['unmute'])
def unmute(bot,message):
    bot_function.unmute_user(bot,message)

@bot.message_handler(commands = ['kick'])
def kick(bot,message):
    bot_function.kick_user(bot,message)

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def predict(message):
    bot_function.predict_bot(bot,message, model_pipeline)

# Запуск бота и закрытие соединения при завершении
try:
    bot.polling(none_stop=True, interval=0)
finally:
    close_connection()