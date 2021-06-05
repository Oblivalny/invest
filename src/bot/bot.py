from telebot import types
import telebot
import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime
from src.app.Assets import Assets
from config.config import db_config
from src.db.db_connect import DataBase

# define Python user-defined exceptions
class Error(Exception):
    """Базовый класс для других исключений"""
    pass

class DateOutsidePeriodError (Error):
    """Возникает, когда входные параметры с датой находится вне целевого периода"""
    pass

class StartDateMoreEndDateError (Error):
    """Возникает, когда входные параметры с датой находится вне целевого периода"""
    pass

class InputParms():
    start_strategy = ''
    end_strategy = ''
    start_period_calculation = ''
    end_period_calculation = ''
    period_holding = ''
    tag = ''

    def set_start_strategy(self, start_strategy):
        self.start_strategy = start_strategy

    def set_end_strategy(self, end_strategy):
        self.end_strategy = end_strategy

    def set_start_period_calculation(self, start_period_calculation):
        self.start_period_calculation = start_period_calculation

    def set_end_period_calculation(self, end_period_calculation):
        self.end_period_calculation = end_period_calculation

    def set_period_holding(self, period_holding):
        self.period_holding = period_holding

    def set_tag(self, tag):
        self.tag = tag

    def validate_start_end_strategy(self):
        if self.start_strategy == '' or self.end_strategy == '':
            return False

        if self.start_strategy > self.end_strategy:
            return False

        return True

    def validate_start_period_calculation(self):
        if not self.validate_start_end_strategy():
            return False

        if self.start_period_calculation == '':
            return False

        if self.start_period_calculation < self.start_strategy or self.start_period_calculation > self.end_strategy:
            return False

        return True

    def validate_end_period_calculation(self):
        if not self.validate_start_end_strategy():
            return False

        if self.end_period_calculation == '':
            return False

        if self.end_period_calculation < self.start_strategy or self.end_period_calculation > self.end_strategy:
            return False

        return True

    def validate_start_end_period_calculation(self):
        if not self.validate_start_period_calculation():
            return False

        if not self.validate_end_period_calculation():
            return False

        if self.start_period_calculation > self.end_period_calculation:
            return False

        return True

    def get_log(self):
        print(f'дата начала проверки стратегии: {self.start_strategy}')
        print(f'дата окончания проверки стратегии: {self.end_strategy}')
        print(f'дата начала периода для расчета: {self.start_period_calculation}')
        print(f'дата окончания периода для расчета: {self.end_period_calculation}')
        print(f'период данных для удержания позиции: {self.period_holding}')
        print(f'выбранный тег: {self.tag}')

    def get_string(self):
        parms = []
        parms.append('Текущие значения параметров:')
        parms.append(f'дата начала проверки стратегии: {self.start_strategy}')
        parms.append(f'дата окончания проверки стратегии: {self.end_strategy}')
        parms.append(f'дата начала периода для расчета: {self.start_period_calculation}')
        parms.append(f'дата окончания периода для расчета: {self.end_period_calculation}')
        parms.append(f'период данных для удержания позиции: {self.period_holding}')
        parms.append(f'выбранный тег: {self.tag}')
        return '\n'.join(parms)

    def is_exists_all_parms(self):
        return (self.start_strategy != '' and self.end_strategy != '' and self.start_period_calculation != '' and self.end_period_calculation != '' and self.period_holding != '' and self.tag != '')


def startCmd(message):
    bot.send_message(message.from_user.id, "Привет! Это чат бот инвестиций.")
    analyzeCmd(message)


def helpCmd(message):
    bot.send_message(message.from_user.id, "Чем я могу тебе помочь?")

    tag = 'AACG'
    start_strategy = datetime(2021, 4, 1, 0, 0, 0)
    end_strategy = datetime(2021, 5, 1, 0, 0, 0)
    period_calculation_start = datetime(2010, 4, 1, 0, 0, 0)
    period_calculation_end = datetime(2021, 5, 1, 0, 0, 0)
    period_holding = 2

    test = Assets(
        tag,
        start_strategy,
        end_strategy,
        period_calculation_start,
        period_calculation_end,
        period_holding
    )
    db = DataBase(db_config['USER_mysql'],
                  db_config['PW_mysql'],
                  db_config['DB_mysql'],
                  db_config['HOST_mysql'])

    test.calculation_balance(db, 5)

    bot.send_message(message.from_user.id, f"""А вот и прогноз  {test.model.pred}""")

    plt.plot(test.model.pred)
    plt.title("Prediction {}".format(input_parms.tag))
    plt.xlabel('day')
    plt.ylabel('price')
    plt.savefig('plot.png')
    plt.clf()

    bot.send_photo(message.chat.id, open('plot.png','rb'))

    stats = []
    stats.append(f'Расширенная статистика')
    stats.append(f'Математическое ожидание: {round(np.mean(test.model.pred),2)}')
    stats.append(f'Дисперсия: {round(np.var(test.model.pred),2)}')

    result = '\n'.join(stats)
    bot.send_message(message.from_user.id, f'{result}')

def getParamsCmd(message):
    bot.send_message(message.from_user.id, input_parms.get_string())


def analyzeCmd(message):
    bot.send_message(message.from_user.id, "Начинаем процесс ввода входных параметров для анализа.")
    bot.send_message(message.from_user.id, "Дата начала проверки стратегии:");
    bot.register_next_step_handler(message, get_start_strategy)


def get_start_strategy(message):
    try:
        x = datetime.strptime(message.text, '%d.%m.%Y')
        input_parms.set_start_strategy(x)
        bot.send_message(message.from_user.id, "Дата окончания проверки стратегии:");
        bot.register_next_step_handler(message, get_end_strategy)
    except ValueError:
        bot.send_message(message.from_user.id, "Неверный формат даты. Ожидается DD.MM.YYYY")
        bot.register_next_step_handler(message, get_start_strategy)

def get_end_strategy(message):
    try:
        x = datetime.strptime(message.text, '%d.%m.%Y')
        input_parms.set_end_strategy(x)

        if not input_parms.validate_start_end_strategy():
            raise StartDateMoreEndDateError

        bot.send_message(message.from_user.id, "Дата начала периода для удержания позиции:");
        bot.register_next_step_handler(message, get_start_period_calculation)
    except ValueError:
        bot.send_message(message.from_user.id, "Неверный формат даты. Ожидается DD.MM.YYYY")
        bot.register_next_step_handler(message, get_end_strategy)
    except StartDateMoreEndDateError:
        bot.send_message(message.from_user.id, "Дата окончания проверки должна быть больше даты начала "
                                               "проверки стратегии")
        bot.register_next_step_handler(message, get_end_strategy)


def get_start_period_calculation(message):
    try:
        x = datetime.strptime(message.text, '%d.%m.%Y')
        input_parms.set_start_period_calculation(x)

        if not input_parms.validate_start_period_calculation():
            raise DateOutsidePeriodError

        bot.send_message(message.from_user.id, "Дата окончания периода для удержания позиции:");
        bot.register_next_step_handler(message, get_end_period_calculation)
    except ValueError:
        bot.send_message(message.from_user.id, "Неверный формат даты. Ожидается DD.MM.YYYY")
        bot.register_next_step_handler(message, get_start_period_calculation)
    except DateOutsidePeriodError:
        bot.send_message(message.from_user.id, "Дата начала периода для удержания позиции должна находиться внутри "
                                               "периода проверки стратегии")
        bot.register_next_step_handler(message, get_start_period_calculation)


def get_end_period_calculation(message):
    try:
        x = datetime.strptime(message.text, '%d.%m.%Y')
        input_parms.set_end_period_calculation(x)

        if not input_parms.validate_end_period_calculation():
            raise DateOutsidePeriodError

        if not input_parms.validate_start_end_period_calculation():
            raise StartDateMoreEndDateError

        bot.send_message(message.from_user.id, "Период для удержания позиции:");
        bot.register_next_step_handler(message, get_period_holding)
    except ValueError:
        bot.send_message(message.from_user.id, "Неверный формат даты. Ожидается DD.MM.YYYY")
        bot.register_next_step_handler(message, get_end_period_calculation)
    except DateOutsidePeriodError:
        bot.send_message(message.from_user.id, "Дата окончания периода для удержания позиции должна находиться внутри "
                                               "периода проверки стратегии")
        bot.register_next_step_handler(message, get_end_period_calculation)
    except StartDateMoreEndDateError:
        bot.send_message(message.from_user.id, "Дата окончания периода для удержания позиции должна быть больше даты "
                                               "начала периода")
        bot.register_next_step_handler(message, get_end_period_calculation)


def get_period_holding(message):
    try:
        x = int(message.text)
        input_parms.set_period_holding(x)
        get_tag(message)
    except ValueError:
        bot.send_message(message.from_user.id, "Неверное значение. Ожидается число")
        bot.register_next_step_handler(message, get_period_holding)


def get_tag(message):
    try:
        db = DataBase(db_config['USER_mysql'],
                      db_config['PW_mysql'],
                      db_config['DB_mysql'],
                      db_config['HOST_mysql'])

        data = db.select_top10_tags()
        tags = data['tag']
        companies = data['company']

        keyboard = types.InlineKeyboardMarkup()

        for i in range(0, len(tags) - 1):
            text = '{} - {}'.format(tags[i], companies[i])
            callback_data = 'tag:{}'.format(tags[i])
            key = types.InlineKeyboardButton(text=text, callback_data=callback_data)
            keyboard.add(key)

        bot.send_message(message.from_user.id, text='Выберите тег компании:', reply_markup=keyboard)
    except ValueError:
        bot.send_message(message.from_user.id, "Произошла ошибка при выборе тега. Повторите попытку")
        bot.register_next_step_handler(message, get_tag)


def final_step_before_run_analyze(message, tag):
    input_parms.set_tag(tag)

    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.chat.id, text='Выполнить анализ?', reply_markup=keyboard)

def analyze(call_message):
    if (not input_parms.is_exists_all_parms()):
        bot.send_message(call_message.chat.id, 'Введены не все входные параметры.')
        return

    # do something and return plots

    bot.send_message(call_message.chat.id, 'Анализ завершен')


botCmds = {
    "/start": startCmd,
    "/help": helpCmd,
    "/analyze": analyzeCmd,
    "/getparams": getParamsCmd,
}

token = '1838702876:AAHaVjvVUkIF3w-20V8RnKnFsd1arEyx7Ps'

input_parms = InputParms()
bot = telebot.TeleBot(token)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  # call.data это callback_data, которая указана при объявлении кнопки
        analyze(call.message)
    elif call.data.startswith("tag:"):
        final_step_before_run_analyze(call.message, call.data[4:])
    else:
        bot.send_message(call.message.chat.id, 'Хорошо, значит в другой раз')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text in botCmds:
        botCmds[message.text](message)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
