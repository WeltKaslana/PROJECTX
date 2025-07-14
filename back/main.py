from flask import Flask, request, Response
from flask_cors import CORS
from waitress import serve
import json
import logging
from datetime import datetime
import pytz, threading
import urllib3

from dao import userDAO
from models import db
from spider import crawler

from sort import ai_get_history, ai_get_keywords, ai_delete_history, ai_recommend
# from sort import test

app = Flask(__name__)
CORS(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/user_db?charset=utf8mb4' #mysql+pymysql://用户名:密码@主机/数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:abc123456@47.98.143.59/user_db?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

http = urllib3.PoolManager(
    maxsize=30,  # 调整为足够处理并发请求的大小
    block=True   # 连接池满时是否阻塞等待
)

db.init_app(app)

# 配置日志格式
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    handlers=[logging.StreamHandler()]
)

# 添加请求日志中间件
@app.before_request
def log_request():
    app.logger.debug('Request: %s %s', request.method, request.path)

@app.after_request
def log_response(response):
    app.logger.debug('Response: %s', response.status_code)
    return response

# 统一JSON响应格式
def json_response(code=200, message="操作成功", result=None, reason=None):
    # 构建响应数据字典，确保包含所有四个字段
    response_data = {
        'code': code,
        'message': message,
        'result': result,
        'reason': reason
    }
    # 直接使用code参数作为HTTP状态码
    status_code = code
    # 序列化为JSON字符串，确保中文正常显示
    json_str = json.dumps(response_data, ensure_ascii=False, indent=2)
    # 返回Response对象
    return Response(json_str, mimetype='application/json', status=status_code)

# 查询历史记录数
@app.route('/historycount/<string:username>', methods=['GET'], strict_slashes=False)
def get_history_count(username):
    if not userDAO.check_username(username):
        res = userDAO.get_history_count(username)
        print('-'*50)
        print(f'{datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}    查询到{username}的历史会话：\n{res}')
        return json_response(message="查询成功",result=res)
    else:
        return json_response(code=404, message="查询失败",reason="用户不存在")

# 查询历史记录c
@app.route('/history/<string:session_id>', methods=['GET'], strict_slashes=False)
def get__history(session_id):
    username, cid = session_id.split("_")
    if userDAO.check(username, cid):
        res = ai_get_history(session_id)
        print('-'*50)
        print(f'{datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}    查询到{session_id}的历史记录：\n{res}')
        return json_response(message="查询成功", result=res)
    else:
        return json_response(code=404, message="查询失败", reason="无此用户或无此会话")
    
# 游客查询
@app.route('/visitor', methods=['GET'], strict_slashes=False)
def visitor():
    nn = userDAO.visitoradd()
    nc = userDAO.newc(nn)
    print('-'*50)
    print(f'{datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}    游客{nn}登录成功，会话ID为：{nc}')
    return json_response(message="游客登录成功", result=[nn, nc])


# 线程安全的爬虫任务
def threaded_crawler(app, key, session_id, nt):
    try:
        # 为每个线程创建应用上下文
        with app.app_context():
            
            # 执行爬取任务
            crawler(app, key, session_id, nt)
            
    except Exception as e:
        # 捕获异常并记录
        print(f"Thread error for key '{key}': {str(e)}")

# 查询结果
@app.route('/keywords/<string:session_id>/<string:question>', methods=['GET'], strict_slashes=False)
def get_keywords(session_id, question):
    print('-'*50)
    print(f'{datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}    收到会话{session_id}的问题{question}')
    
    # keys, flag = ai_get_keywords(session_id, question) #调用AI获取关键词
    keys = ['手机','手表']
    flag = 1

    if flag:
        nt = userDAO.new_talk_id(session_id)

        threads =[]

        for key in keys: #根据关键词爬取网站，结果以json返回
            thread = threading.Thread(
                target=threaded_crawler, 
                args=(app, key, session_id, nt)
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

        tip = "我认为你可能需要的商品是 "
        res = '_'.join(keys)
        return json_response(message=tip+','.join(keys), result=res)
    else:
        keys = userDAO.find_keys(session_id)
        res = '_'.join(keys)
        return json_response(message=None, result=res)
    

thread_local = threading.local()
@app.route('/result/<string:session_id>/<string:question>/<string:keys>', methods=['GET'], strict_slashes=False)
def get_result(session_id, question, keys):
    key_list = keys.split("_")
    print('-'*50)
    print(f'{datetime.now(pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")}    正在对会话{session_id}的问题‘{question}’进行推荐')
    
    # 为当前请求创建独立的结果列表
    results = []
    lock = threading.Lock()
    
    def worker(app, session_id, question, key):
        try:
            with app.app_context():
                res = ai_recommend(session_id=session_id, question=question, key=key)
                # res = 1
                print(res)
                with lock:
                    results.append(res)
        except Exception as e:
            print(f"Thread error for key '{key}': {str(e)}")

    threads = []
    for key in key_list:
        t = threading.Thread(target=worker, args=(app, session_id, question, key))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    if not hasattr(thread_local, 'results'):
        thread_local.results = []

    return json_response(message="得到推荐结果", result=results)
# 删除历史记录
@app.route('/delete/<string:session_id>', methods=['GET'], strict_slashes=False)
def delete(session_id):
    username, cid = session_id.split("_")
    if userDAO.check(username, cid):
        ai_delete_history(session_id)
        userDAO.delete_history(session_id)
        print('-'*50)
        print(f'{datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}    删除了会话{session_id}')
        return json_response(message="删除成功")
    else:
        return json_response(code=500, message="删除失败", reason="无此会话")

# 注册用户
@app.route('/register/<string:username>/<string:password>', methods=['GET'], strict_slashes=False)
def register(username, password):
    print('-'*50)
    print(f'{datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}    注册用户{username}, 密码{password}')
    if userDAO.check_username(username):
        userDAO.add_user(username, password)
        return json_response(message="注册成功")
    else:
        return json_response(code=500, message="注册失败", reason="用户名已存在或非法")
    
    
# 登录
@app.route('/login/<string:username>/<string:password>', methods=['GET'], strict_slashes=False)
def login(username, password):
    print('-'*50)
    print(f'{datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}    用户{username}登录, 密码{password}')
    if userDAO.checklog(username, password):
        return json_response(message="登录成功")
    else:
        return json_response(code=500, message="登录失败", reason="用户名或密码错误")
    
    
# 新对话
@app.route('/new/<string:username>', methods=['GET'], strict_slashes=False)
def new(username):
    print(username)
    if not userDAO.check_username(username):
        nc = userDAO.newc(username)
        print('-'*50)
        print(f'{datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}    用户{username}创建了新会话{nc}')
        return json_response(message="创建成功", result=nc)
    else:
        return json_response(code=500, message="新对话创建失败", reason="用户不存在")

@app.route('/test', methods=['GET'], strict_slashes=False)
def main_test():
    print(f'{datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}    testing...')
    # test()
    return json_response(message="test")

if __name__ == '__main__':
    # app.run(debug=True)
    # 创建数据库表
    try:
        with app.app_context():
            db.create_all()
            app.logger.info('Database tables created successfully.')
    except Exception as e:
        app.logger.error(f'Error creating database tables: {e}')

    serve(app, host='0.0.0.0', port=8080, threads=4)
    