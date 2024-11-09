from telebot import TeleBot
import time
from database_using import save_user, log_message

def start_bot(bot: TeleBot, message):
    bot.reply_to(message, "Привет! Я - бот для удаления токсичных комментариев и модерации сервера. Напиши /help, чтобы узнать больше.")

def help_bot(bot: TeleBot, message):
    bot.reply_to(message, "Я - бот для удаления токсичных комментариев и модерации сервера. Я автоматически удаляю токсичные комментарии. Если человек ведет себя слишком токсично, я временно лишаю его возможности писать в чат. У меня предусмотрены команды для ручной модерации: /mute - замутить пользователя на определенное время\n/unmute - размутить пользователя")


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

def mute_user_bot(bot: TeleBot, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status

        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно замутить администратора.")
        else:
            duration = 60 # Значение по умолчанию - 1 минута

            bot.restrict_chat_member(chat_id, user_id, until_date=time.time()+duration)
            bot.reply_to(message, f"Пользователь {message.from_user.username} замучен на {duration} секунд.")

def unmute_user(bot: TeleBot, message):
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
def predict_bot(bot: TeleBot,message, model_pipeline):

    # Предсказание с использованием модели
    print('Идет обработка')
    prediction = int((model_pipeline.predict([message.text])))
    if prediction == 1:
        is_toxic = True
        bot.send_message(message.from_user.id,
                         f"Ваше сообщение было удалено, так как оно определено как токсичное. Пожалуйста, соблюдайте правила общения.")
        mute_user_bot(bot, message)
        # Удаление сообщения, если оно токсично
        bot.delete_message(message.chat.id, message.message_id)
        save_user(message.from_user.id, message.from_user.username, is_toxic)
        log_message(message.from_user.id, message.from_user.username, message.text, is_toxic)
    else:
        is_toxic = False
        save_user(message.from_user.id, message.from_user.username, is_toxic)
        log_message(message.from_user.id, message.from_user.username, message.text, is_toxic)


