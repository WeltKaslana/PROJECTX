from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'User'

    username = db.Column(db.String(20), primary_key=True, autoincrement=False) # 用户名
    password = db.Column(db.String(20), nullable=False) # 密码
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp()) # 注册时间

class History(db.Model):
    __tablename__ = 'History'

    username = db.Column(db.String(20), nullable=False) # 用户名
    conversation_id = db.Column(db.String(4), nullable=False) # 会话ID
    session_id = db.Column(db.String(25), primary_key=True, autoincrement=False) # 会话ID
    # session_id = f'{username}:{conversation_id:4d}
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp()) # 创建时间