from models import db, User, History, Goods
import random
from sqlalchemy import func

def check_re(username: str):
    import re
    pattern = r'^[a-zA-Z0-9-]+$'
    if re.match(pattern, username) and not username.startswith('visitor'):
        return True
    else:
        return False
        
class userDAO():
    
    @staticmethod 
    # 检查用户名是否已存在, 检查用户名只能包含字母数字和符号-
    # 若用户不存在则返回True
    # 返回bool
    def check_username(username: str):
        if check_re(username):
            user = User.query.filter_by(username=username).first()
            return user is None
        else:
            return False
    
    @staticmethod # 查询是否有这个用户名和会话id，返回bool
    def check(username: str, cid: str):
        history = History.query.filter_by(username=username, conversation_id=cid).first()
        return history is not None

    @staticmethod # 增加新用户
    def add_user(username: str, password: str):
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

    @staticmethod # 检查用户名和密码，返回bool
    def checklog(username: str, password: str):
        user = User.query.filter_by(username=username, password=password).first()
        return user is not None

    @staticmethod #获得一个不重复的visitor_id，4位数字
    def visitoradd():
        while True:
            visitor_id = str(random.randint(1000, 9999))
            if User.query.filter_by(username=f'visitor{visitor_id}').first() is None:
                break
        user = User(username=f'visitor{visitor_id}', password='visitor')
        db.session.add(user)
        db.session.commit()
        return f'visitor{visitor_id}'

    @staticmethod # 获得一个会话id，不同用户独立编号
    def newc(username: str):
        last_history = History.query.filter_by(username=username).order_by(History.conversation_id.desc()).first()
        if last_history:
            last_cid = int(last_history.conversation_id)
            new_cid = str(last_cid + 1).zfill(4)
        else:
            new_cid = '0001'
        db.session.add(History(username=username, conversation_id=new_cid, session_id=f'{username}_{new_cid}'))  
        db.session.commit()
        return f'{username}_{new_cid}'
    
    def get_history_count(username: str):
        res = History.query.filter_by(username=username).all()
        session_ids = [result.session_id for result in res]
        return session_ids
    
    def delete_history(session_id: str):
        History.query.filter_by(session_id=session_id).delete()

    # def add_goods(session_id: str, name: str, price: float, img_url: str, shop_url: str, goods_url: str, deals: int):
    #     db.session.add(Goods(
    #         session_id=session_id, 
    #         name=name, price=price, 
    #         img_url=img_url, 
    #         shop_url=shop_url, 
    #         goods_url=goods_url, 
    #         deals=deals))
    #     db.session.commit()

    def add_goods(session_id: str, 
                  talk_id: int, 
                  keyword: str, 
                  name: str, 
                  price: float, 
                  deals: int,
                  goods_url: str,
                  shop_url: str, 
                  img_url: str, 
                  ):
        db.session.add(Goods(
            session_id=session_id,
            talk_id = talk_id,
            keyword = keyword,
            name = name,
            price = price,
            deals = deals,
            goods_url = goods_url,
            shop_url=shop_url,
            img_url=img_url,
        ))
        db.session.commit()

    def new_talk_id(session_id: str):
        last_id = Goods.query.filter_by(session_id=session_id).order_by(Goods.talk_id.desc()).first()
        if last_id:
            last_cid = int(last_id.talk_id)
            new_cid = last_cid + 1
        else:
            new_cid = 1
        return new_cid


    # def find_goods(session_id: str):
    #     query_res = Goods.query.filter_by(session_id=session_id).all()
    #     goods = []
    #     for good in query_res:
    #         good_data = {
    #             'name': good.name,
    #             'price': good.price,
    #             'deals': good.deals,
    #             'img_url': good.img_url,
    #             'goods_url': good.goods_url,
    #             'shop_url': good.shop_url,
    #         }
    #         goods.append(good_data)
    #     return goods

    def find_goods(session_id: str, keyword: str):
        subquery = db.session.query(
            func.max(Goods.talk_id)
        ).filter_by(session_id=session_id, keyword=keyword).scalar_subquery()
        goods_list = Goods.query.filter(
            Goods.session_id == session_id,
            Goods.keyword == keyword,
            Goods.talk_id == subquery
        ).all()
        goods = []
        for good in goods_list:
            goods.append({
                'name': good.name,
                'price': good.price,
                'deals': good.deals,
                'goods_url': good.goods_url,
                'shop_url': good.shop_url,
                'img_url': good.img_url,
            })
        return goods
    
    def find_keys(session_id: str):
        subquery = db.session.query(
            func.max(Goods.talk_id)
        ).filter_by(session_id=session_id).scalar_subquery()
        res = db.session.query(Goods.keyword).filter_by(
            session_id=session_id,
            talk_id = subquery).distinct().all()
        return [key[0] for key in res]
