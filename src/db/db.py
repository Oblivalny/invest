from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

Base = declarative_base()


class Assets(Base):

    __tablename__ = 'assets'
    tag = Column(String(50), primary_key=True)
    company = Column(String(50))
    last_update = Column(DATETIME)
    last_values = (Integer)

    def __init__(self, tag, company, last_update, last_values):
        self.tag = tag
        self.company = company
        self.last_update = last_update
        self.last_values = last_values

    def __repr__(self):
        return "<Good('%s','%s', '%s', '%s')>" % (self.tag, self.company, self.last_update,
                                                  self.last_values)


class Quotes_history(Base):

    __tablename__ = 'quotes_history'
    id = Column(Integer, primary_key=True)
    tag = Column(String(50), ForeignKey('assets.tag'))
    date = Column(DATETIME)
    open = Column(Integer)
    high = Column(Integer)
    low = Column(Integer)
    close = Column(Integer)
    adj_close = Column(Integer)
    volume = Column(Integer)

    def __init__(self, tag, date, open, high, low, close,  adj_close, volume):
        self.tag = tag
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.adj_close = adj_close
        self.volume = volume

    def __repr__(self):
        return "<Good('%s','%s', '%s','%s', '%s','%s', '%s','%s')>" % \
               (self.tag, self.date, self.open, self.high,
                self.low, self.close, self.adj_close, self.volume)


class Users_favorite_assets(Base):

    __tablename__ = 'Users_favorite_assets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'))
    tag = Column(String(50), ForeignKey('assets.tag'))
    date = Column(DATETIME)
    start_strategy = Column(DATETIME)
    end_strategy = Column(DATETIME)
    period_calculation = Column(DATETIME)
    period_holding = Column(DATETIME)
    balance = Column(Integer)
    # можно еще график хранить

    def __init__(self, user_id, tag, date, start_strategy,
                 end_strategy, period_calculation, period_holding, balance):
        self.user_id = user_id
        self.tag = tag
        self.date = date
        self.start_strategy = start_strategy
        self.end_strategy = end_strategy
        self.period_calculation = period_calculation
        self.period_holding = period_holding
        self.balance = balance

    def __repr__(self):
        return "<Good('%s', '%s','%s', '%s','%s', '%s','%s', '%s')>" % \
               (self.user_id, self.tag, self.date, self.start_strategy,
                self.end_strategy, self.period_calculation,
                self.period_holding, self.balance)

class Users(Base):

    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    telegram_chat_id = Column(Integer)

    def __init__(self, telegram_id, telegram_chat_id):
        self.telegram_id = telegram_id
        self.telegram_chat_id = telegram_chat_id

    def __repr__(self):
        return "<Good('%s','%s')>" % (self.telegram_id, self.telegram_chat_id)


def connect(user, pwd, host='localhost', echo=True):
    return create_engine(f"""mysql+pymysql://{user}:{pwd}@{host}/test""", echo=echo, pool_pre_ping=True)


def migration(engine):
    Base.metadata.create_all(engine)


def create_session(engine):
    return sessionmaker(bind=engine)()