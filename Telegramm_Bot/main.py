import telebot
import config
import extensions

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f"Приветствую, {message.chat.first_name}")
    bot.send_message(message.chat.id, 'Для того, что бы воспользоваться ботом, введите:\n"название первой валюты"'
                                      ' "название второй валюты" "количество первой валюты"')


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, 'Для того, что бы воспользоваться ботом, введите:\n"название первой валюты"'
                                      ' "название второй валюты" "количество первой валюты"')


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in config.currency_list:
        h = config.currency_list[key][0]
        h = str(h).title()
        text += '\n' + h
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def answer(message: telebot.types.Message):
    try:
        bot.reply_to(message, extensions.MessageHandler.message_recipient(message.text))
    except extensions.APIException as e:
        bot.reply_to(message, f"Ошибка в команде:\n{e}")



bot.polling(none_stop=True)
