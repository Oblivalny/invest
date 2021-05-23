from sklearn.metrics import mean_squared_error
import xgboost as xgb
import pandas as pd
import numpy as np


class Model(object):

    def __init__(self, data, lag_start, lag_end, test_size=0.2):
        self.data = data
        self.lag_start = lag_start
        self.lag_end = lag_end
        self.test_size = test_size
        self.bst = None
        self.pred = None
        self.score = None

    def code_mean(self, data, cat_feature, real_feature):
        """
        Возвращает словарь, где ключами являются уникальные категории признака cat_feature,
        а значениями - средние по real_feature
        """
        return dict(data.groupby(cat_feature)[real_feature].mean())

    def prepare_data(self, train=True):

        if not train:
            dfg = pd.DataFrame()
            data = self.data.to_list()
            data.reverse()
            for i in range(0, self.lag_end - self.lag_start):
                dfg["lag_{}".format(i + self.lag_start)] = data[i:self.lag_start + i]
            return dfg

        data = pd.DataFrame(self.data.copy())

        # считаем индекс в датафрейме, после которого начинается тестовыый отрезок
        test_index = int(len(data) * (1 - self.test_size))

        # добавляем лаги исходного ряда в качестве признаков
        for i in range(self.lag_start, self.lag_end):
            data["lag_{}".format(i)] = data["Adj Close"].shift(i)

        data = data.dropna()
        data = data.reset_index(drop=True)

        # разбиваем весь датасет на тренировочную и тестовую выборку
        X_train = data.loc[:test_index].drop(["Adj Close"], axis=1)
        y_train = data.loc[:test_index]["Adj Close"]
        X_test = data.loc[test_index:].drop(["Adj Close"], axis=1)
        y_test = data.loc[test_index:]["Adj Close"]

        return X_train, X_test, y_train, y_test

    def XGB_forecast(self, scale=1.96):
        # исходные данные
        X_train, X_test, y_train, y_test = self.prepare_data(self.data)
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test)

        # задаём параметры
        params = {
            'objective': 'reg:squarederror',
            'booster': 'gblinear',
            'learning_rate': 0.3
        }

        trees = 1000

        # прогоняем на кросс-валидации с метрикой rmse
        cv = xgb.cv(params, dtrain, metrics=('rmse'), verbose_eval=False, nfold=5, show_stdv=False, num_boost_round=trees)

        # обучаем xgboost с оптимальным числом деревьев, подобранным на кросс-валидации
        bst = xgb.train(params, dtrain, num_boost_round=cv['test-rmse-mean'].argmin())

        # можно построить кривые валидации
        #     cv.plot(y=['test-mae-mean', 'train-mae-mean'])

        # запоминаем ошибку на кросс-валидации
        deviation = cv.loc[cv['test-rmse-mean'].argmin()]["test-rmse-mean"]

        # посмотрим, как модель вела себя на тренировочном отрезке ряда
        # prediction_train = bst.predict(dtrain)
        # plt.figure(figsize=(15, 5))
        # plt.plot(prediction_train)
        # plt.plot(y_train)
        # plt.axis('tight')
        # plt.grid(True)

        # и на тестовом
        prediction_test = bst.predict(dtest)
        lower = prediction_test - scale * deviation
        upper = prediction_test + scale * deviation

        Anomalies = np.array([np.NaN] * len(y_test))
        Anomalies[y_test < lower] = y_test[y_test < lower]

        # plt.figure(figsize=(25, 10))
        # plt.plot(prediction_test, label="prediction")
        # #     plt.plot(lower, "r--", label="upper bond / lower bond")
        # #     plt.plot(upper, "r--")
        # plt.plot(list(y_test), label="y_test")
        # #     plt.plot(Anomalies, "ro", markersize=10)
        # plt.legend(loc="best")
        # plt.axis('tight')
        # plt.title("XGBoost Mean absolute error {} users".format(round(mean_absolute_error(prediction_test, y_test))))
        # plt.grid(True)
        # plt.legend()

        self.score(mean_squared_error(y_test, prediction_test))

        df_pred = self.prepare_data(train=False)
        df_pred = xgb.DMatrix(df_pred)

        bst.predict(df_pred)
        pred = list(bst.predict(df_pred))
        pred.reverse()