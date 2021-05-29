# from src.db.db_connect import *
#
#
# class User(object):
#
#     def __init__(self, id_telegram=None, id_chat=None):
#         self.id_telegram = id_telegram
#         self.id_chat = id_chat
#
#     def save_assets(self, conn, assets):
#         user_id = conn.session.query(Users).filter(
#             Users.telegram_id == self.id_telegram).first().id
#         new_favorite_assets = Users_favorite_assets(
#             user_id=user_id,
#             tag=assets.tag,
#             date=datetime.now(),
#             start_strategy=assets.start_strategy,
#             end_strategy=assets.end_strategy,
#             period_calculation=assets.period_calculation,
#             period_holding=assets.period_holding,
#             balance=assets.balance)
#
#         conn.session.add(new_favorite_assets)
#         conn.session.commit()