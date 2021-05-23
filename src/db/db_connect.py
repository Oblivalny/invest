from src.db.db import *
from datetime import datetime
import yfinance as yf


class DataBase(object):
    def __init__(self, username='root', pw='root', echo=False, migration_db=True):
        self.engine = connect(username, pw, echo=echo)
        self.session = create_session(self.engine)
        if migration_db:
            migration(self.engine)

    def close(self):
        self.session.close()
        self.engine.dispose()

    def update_data(self, tag):
        last_update = self.session.query(Assets).filter(Assets.tag == tag).first().last_update
        if last_update != datetime.now().date():
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

    def select_adj_close(self, tag):
        data = []
        for good in self.session.query(Quotes_history).filter(Quotes_history.tag == tag).all():
            data.append(good.adj_close)

        return data


