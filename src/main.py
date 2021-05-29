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
while True:
    bot.polling(none_stop=True, interval=0)