from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'User'

    username = db.Column(db.String(20), primary_key=True, autoincrement=False) # 用户名
    password = db.Column(db.String(20), nullable=False) # 密码
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp()) # 注册时间

class History(db.Model):
    __tablename__ = 'History'

    username = db.Column(db.String(20), db.ForeignKey('User.username'), nullable=False) # 用户名
    conversation_id = db.Column(db.String(4), nullable=False) # 会话ID
    session_id = db.Column(db.String(25), primary_key=True, autoincrement=False) # 会话ID
    # session_id = f'{username}:{conversation_id:4d}
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp()) # 创建时间

class Goods(db.Model):
    __tablename__ = 'Goods'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(25), db.ForeignKey('History.session_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    deals = db.Column(db.Integer, nullable=False)
    goods_url = db.Column(db.String(300), nullable=False)
    shop_url = db.Column(db.String(300), nullable=False)
    img_url = db.Column(db.String(300), nullable=False)
