
import telebot
import time
import cloudpickle

import json
from datetime import datetime
import psycopg2
from psycopg2 import sql

from dotenv import load_dotenv
import os

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

#stats = {} словарь для хранения статистики

# импорт файла с моделью

with open('model.pkl', 'rb') as f:
    model_pipeline = cloudpickle.load(f)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я - бот для удаления токсичных комментариев и модерации сервера. Напиши /help, чтобы узнать больше.")



@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "Я - бот для удаления токсичных комментариев и модерации сервера. Я автоматически удаляю токсичные комментарии. Если человек ведет себя слишком токсично, я временно лишаю его возможности писать в чат. У меня предусмотрены команды для ручной модерации: /mute - замутить пользователя на определенное время\n/unmute - размутить пользователя")

def log_message(user_id, username, message, is_toxic):
    log_entry = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "user_id": user_id,
        "username": username,
        "message": message,
        "is_toxic": is_toxic
    }

    # Запись в файл (например, log.json)
    with open("log.json", "a" , encoding = 'utf-8') as log_file:
        log_file.write(json.dumps(log_entry, ensure_ascii = False) + "\n")


def save_user(user_id, username, is_toxic):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            host=os.getenv("HOST"),
            port=os.getenv("PORT")
        )
        cursor = conn.cursor()
        print("Соединение с базой данных успешно установлено!")

    except psycopg2.OperationalError as e:
        print("Не удалось подключиться к базе данных!")
        print("Ошибка:", e)

    cursor.execute("SELECT toxic_count FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    if result:
        if is_toxic:
            new_count = int(result[0] + 1)
            cursor.execute("UPDATE users SET toxic_count = %s WHERE user_id = %s", (new_count, user_id,))
    '''else:
        toxic_count = 1 if is_toxic else 0
        cursor.execute(
            "INSERT INTO users (user_id, username, toxic_count) VALUES (%s,%s,%s)", (user_id, username, toxic_count,)
        )'''

    conn.commit()
    # Закрываем соединение при завершении работы бота
    cursor.close()
    conn.close()

'''@bot.message_handler(commands=['kick'])
def kick_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно кикнуть администратора.")
        else:
            bot.kick_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} был кикнут.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите кикнуть.")
'''

@bot.message_handler(commands=['mute'])
def mute_user(message):
    #if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status

        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно замутить администратора.")
        else:
            duration = 60 # Значение по умолчанию - 1 минута

            bot.restrict_chat_member(chat_id, user_id, until_date=time.time()+duration)
            bot.reply_to(message, f"Пользователь {message.from_user.username} замучен на {duration} секунд.")
    #else:
        #bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите замутить.")


@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} размучен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите размутить.")

'''@bot.message_handler(commands=['stats'])
def chat_stats(message):
    chat_id = message.chat.id
    if chat_id not in stats:
        bot.reply_to(message, "Статистика чата пуста.")
    else:
        total_messages = stats[chat_id]['total_messages']
        unique_users = len(stats[chat_id]['users'])
        bot.reply_to(message, f"Статистика чата:\nВсего сообщений: {total_messages}\nУникальных пользователей: {unique_users}")


@bot.message_handler(commands=['selfstat'])
def user_stats(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    if chat_id not in stats:
        bot.reply_to(message, "Статистика чата пуста.")
    else:
        if user_id not in stats[chat_id]['users']:
            bot.reply_to(message, "Вы еще не отправляли сообщений в этом чате.")
        else:
            user_messages = stats[chat_id]['users'][user_id]['messages']
            total_messages = stats[chat_id]['total_messages']
            percentage = round(user_messages / total_messages * 100, 2)
            bot.reply_to(message, f"Статистика для пользователя @{username}:\nВсего сообщений: {user_messages}\nПроцент от общего количества сообщений: {percentage}%")
'''
@bot.message_handler(func = lambda message :not message.text.startswith('/'))
def predict(message):
    # Прогноз для комментария от пользователя

    print('Идет обработка')
    # Предсказание с использованием вашей модели
    prediction = int((model_pipeline.predict([message.text])))
    if prediction == 1:
        is_toxic = True
        bot.reply_to(message,f'Ваш комментарий токсичен. Не делайте так больше😥')
        mute_user(message)
        log_message(message.from_user.id, message.from_user.username, message.text, is_toxic)
        save_user(message.from_user.id, message.from_user.username, is_toxic)
        '''is_muted = save_user(message.from_user.id, message.from_user.username, True)
      if is_muted:
          bot.reply_to(message, 'Вы были замучены за токсичные комментарии.')'''
    else:
        is_toxic = False
        bot.reply_to(message,f'Ваш комментарий не токсичен. Вы молодец!😁')
        log_message(message.from_user.id, message.from_user.username, message.text, is_toxic)
        save_user(message.from_user.id, message.from_user.username, is_toxic)



bot.polling(none_stop=True, interval=0)