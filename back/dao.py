from models import db, User, History
import random

class userDAO():

    @staticmethod 
    # 检查用户名是否已存在, 检查用户名只能包含字母数字和符号-
    # 返回bool
    def check_username(username: str):
        import re
        pattern = r'^[a-zA-Z0-9-]+$'
        if not re.match(pattern, username) or username.startswith('visitor'):
            return False
        user = User.query.filter_by(username=username).first()
        return user is None

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