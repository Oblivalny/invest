from src.db.db import *
from datetime import datetime, timedelta
import yfinance as yf


class DataBase(object):

    def __init__(self, username='root', pw='root', db='invest_bot', host='localhost',
                 echo=False, migration_db=False):
        self.engine = self.__connect__(username, pw, db, host, echo=echo)
        self.session = self.__create_session__(self.engine)
        if migration_db:
            self.__migration__(self.engine)

    def __connect__(self, user, pwd, db='invest_bot', host='localhost', echo=True):
        return create_engine(f"""mysql+pymysql://{user}:{pwd}@{host}/{db}""", echo=echo, pool_pre_ping=True)

    def __create_session__(self, engine):
        return sessionmaker(bind=engine)()

    def __migration__(self, engine):
        Base.metadata.create_all(engine)
        if self.session.query(Assets).first() is None:
            self.__load_assets_table__()

    def __load_assets_table__(self):
        df = pd.read_csv('src/db/Assets_table.csv')
        df.last_update = pd.to_datetime(df.last_update)

        for index, row in df.iterrows():
            new_row = Assets(
                tag=row['tag'],
                company=row['company'],
                last_update=row['last_update'],
                last_values=row['last_values']
            )
            self.session.add(new_row)
        self.session.commit()
        self.session.close()

    def close(self):
        self.session.close()
        self.engine.dispose()

    def update_data(self, tag):
        last_update = self.session.query(Assets).filter(Assets.tag == tag).first().last_update
        if last_update.date() != datetime.now().date()-timedelta(days=1):
            df = yf.download(tag, last_update, datetime.now().date())

            for index, row in df.iterrows():
                new_row = Quotes_history(
                    tag=tag,
                    date=index,
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    adj_close=row['Adj Close'],
                    volume=row['Volume'])

                self.session.add(new_row)
            self.session.commit()

            last_update = df.index.max()
            last_values = df[df.index == df.index.max()]['Adj Close'].values[0]

            self.session.query(Assets).filter(Assets.tag == tag).update(
                {Assets.last_update: last_update, Assets.last_values: last_values}, synchronize_session=False)
            self.session.commit()


    def select_adj_close(self, tag, start_date, end_date):
        data = {'date':[], 'Adj Close':[]}

        for val in self.session.query(Quotes_history).filter(
                Quotes_history.tag == tag,
                Quotes_history.date >= start_date,
                Quotes_history.date <= end_date).all():

            data['Adj Close'].append(val.adj_close)
            data['date'].append(val.date)

        return data