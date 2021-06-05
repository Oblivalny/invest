from src.model.model import *


class Assets(object):

    def __init__(self, tag, start_strategy, end_strategy, period_calculation_start,
                 period_calculation_end, period_holding):

        self.tag = tag
        self.start_strategy = start_strategy
        self.end_strategy = end_strategy
        self.period_calculation_start = period_calculation_start
        self.period_calculation_end = period_calculation_end
        self.period_holding = period_holding
        self.balance = None
        self.maximum_drawdown = None
        self.model = None

    def calculation_balance(self, db, assets_cnt):
        """" Расчет баланса
            conn - подключение к базе
            assets_cnt - кол-во акций
        """

        # Обновляем данные в БД. Собираем актуальную инфу до сегодняшнего дня
        db.update_data(self.tag)

        # Отбор данный за конкретный период для обучения модели "период данных для расчета"
        data = pd.DataFrame(db.select_adj_close(self.tag,
                                     self.period_calculation_start,
                                     self.period_calculation_end))
        data = data.sort_values('date')
        # print(data.shape)
        lag_start = (self.end_strategy-self.start_strategy).days
        lag_end = (self.end_strategy-self.start_strategy).days*2
        self.model = Model(data['Adj Close'], lag_start, lag_end)
        self.model.XGB_forecast()
        prediction = self.model.pred
        self.balance = self.get_balance(prediction, self.period_holding)
        self.maximum_drawdown = self.get_maximum_drawdown(prediction)
        print(prediction)


    # def save_favorite_assets(self, session, user_id):
    #
    #     new_favorite_assets = Users_favorite_assets(
    #         user_id=user_id, tag=self.tag, date=datetime.now(), start_strategy=self.start_strategy,
    #         end_strategy=self.end_strategy, period_calculation=self.period_calculation,
    #         period_holding=self.period_holding, balance=self.balance)
    #
    #     session.add(new_favorite_assets)
    #     session.commit()

    def get_balance(self, predict, holding):
        result = []

        i = 0
        j = 0
        iter_sum = 0
        prev_value = predict[0]
        iter = round(len(predict) / holding) - 1

        for e in predict:
            iter_sum = iter_sum + (e - prev_value)
            prev_value = e

            # print(e)
            if i < iter:
                i = i + 1
            else:
                i = 0
                result.append(abs(iter_sum))
                iter_sum = 0
                # print('')

            j = j + 1

            if j == len(predict):
                result.append(iter_sum)

        balance = sum(result)
        return balance, result

    def get_maximum_drawdown(self, predict):
        """ Максимальная просадка(MDD) – это показатель наибольшего падения цены актива от пика до минимума. """
        iter_sum = 0
        i = 0
        prev_value = predict[0]
        result = []

        for vl in predict:

            if vl <= prev_value:
                iter_sum = iter_sum + (prev_value - vl)
            elif iter_sum > 0:
                result.append(iter_sum)
                iter_sum = 0
            else:
                iter_sum = 0

            prev_value = vl

            i = i + 1

            if i == len(predict):
                result.append(iter_sum)

        return max(result)