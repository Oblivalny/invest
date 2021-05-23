from src.db.db import *
from src.model.model import *
from datetime import datetime


class Assets(object):

    def __init__(self, tag, start_strategy, end_strategy, period_calculation, period_holding):
        self.tag = tag
        self.start_strategy = start_strategy
        self.end_strategy = end_strategy
        self.period_calculation = period_calculation
        self.period_holding = period_holding
        self.balance = None
        self.model = None

    def calculation_balance(self, conn, assets_cnt):
        conn.update_data(self.tag)

        #  Тут нужно быть внимательным. Пероверить после уточнений Мельникова
        data = conn.select_adj_close(self.tag)
        lag_start = int((self.end_strategy-self.start_strategy).day)
        lag_end = int((self.end_strategy-self.start_strategy).day)*2
        self.model = Model(data, lag_start, lag_end)
        self.model.XGB_forecast()
        prediction = self.model.pred
        self.balance = assets_cnt*prediction[-1]

    def save_favorite_assets(self, session, user_id):

        new_favorite_assets = Users_favorite_assets(
            user_id=user_id, tag=self.tag, date=datetime.now(), start_strategy=self.start_strategy,
            end_strategy=self.end_strategy, period_calculation=self.period_calculation,
            period_holding=self.period_holding, balance=self.balance)

        session.add(new_favorite_assets)
        session.commit()