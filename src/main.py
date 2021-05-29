from src.db.db import *
from src.bot.bot import *


# token = '1838702876:AAHaVjvVUkIF3w-20V8RnKnFsd1arEyx7Ps'

# БД
USER_mysql = 'root'
PW_mysql = 'root'
DB_mysql = 'invest_bot'
HOST_mysql = 'localhost'

engine = connect(USER_mysql, PW_mysql, DB_mysql, HOST_mysql)
migration(engine)
session = create_session(engine)
migration(engine)


#  Бот
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  # call.data это callback_data, которая указана при объявлении кнопки
        analyze(call.message)
    else:
        bot.send_message(call.message.chat.id, 'Хорошо, значит в другой раз')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text in botCmds:
        botCmds[message.text](message)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")




