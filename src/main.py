from src.db.db_connect import DataBase
from src.bot.bot import bot
from config.config import db_config

# БД
db = DataBase(db_config['USER_mysql'],
              db_config['PW_mysql'],
              db_config['DB_mysql'],
              db_config['HOST_mysql'], migration_db=True)

#  Бот
while True:
    bot.polling(none_stop=True, interval=0)


