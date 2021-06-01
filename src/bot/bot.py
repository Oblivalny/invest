from telebot import types
import telebot
from datetime import datetime, timedelta
from src.app.Assets import Assets
from config.config import db_config
from src.db.db_connect import DataBase

class InputParms():
    start_strategy = ''
    end_strategy = ''
    period_calculation = ''
    period_holding = ''

    def set_start_strategy(self, start_strategy):
        self.start_strategy = start_strategy

    def set_end_strategy(self, end_strategy):
        self.end_strategy = end_strategy

    def set_period_calculation(self, period_calculation):
        self.period_calculation = period_calculation

    def set_period_holding(self, period_holding):
        self.period_holding = period_holding

    def get_log(self):
        print(f'дата начала проверки стратегии: {self.start_strategy}')
        print(f'дата окончания проверки стратегии: {self.end_strategy}')
        print(f'период данных для расчета: {self.period_calculation}')
        print(f'период данных для удержания позиции: {self.period_holding}')

    def get_string(self):
        parms = []
        parms.append('Текущие значения параметров:')
        parms.append(f'дата начала проверки стратегии: {self.start_strategy}')
        parms.append(f'дата окончания проверки стратегии: {self.end_strategy}')
        parms.append(f'период данных для расчета: {self.period_calculation}')
        parms.append(f'период данных для удержания позиции: {self.period_holding}')
        return '\n'.join(parms)

    def is_exists_all_parms(self):
        return (self.start_strategy != '' and self.end_strategy != '' and
                    self.period_calculation != '' and self.period_holding != '')


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




def getParamsCmd(message):
    bot.send_message(message.from_user.id, input_parms.get_string())


def analyzeCmd(message):
    bot.send_message(message.from_user.id, "Начинаем процесс ввода входных параметров для анализа.")
    bot.send_message(message.from_user.id, "Дата начала проверки стратегии:");
    bot.register_next_step_handler(message, get_start_strategy)


def get_start_strategy(message):
    input_parms.set_start_strategy(message.text)
    bot.send_message(message.from_user.id, "Дата окончания проверки стратегии:");
    bot.register_next_step_handler(message, get_end_strategy)


def get_end_strategy(message):
    input_parms.set_end_strategy(message.text)
    bot.send_message(message.from_user.id, "Период данных для расчета:");
    bot.register_next_step_handler(message, get_period_calculation)


def get_period_calculation(message):
    input_parms.set_period_calculation(message.text)
    bot.send_message(message.from_user.id, "Период данных для удержания позиции:")
    bot.register_next_step_handler(message, get_period_holding)


def get_period_holding(message):
    input_parms.set_period_holding(message.text)
    bot.send_message(message.from_user.id, "Ввод параметров завершен.")

    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, text='Выполнить анализ?', reply_markup=keyboard)


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
    else:
        bot.send_message(call.message.chat.id, 'Хорошо, значит в другой раз')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text in botCmds:
        botCmds[message.text](message)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")




