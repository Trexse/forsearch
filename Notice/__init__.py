from flask import Flask
from .config import config_map
from flask_sqlalchemy import SQLAlchemy
import redis

# 数据库
db = SQLAlchemy()

# 创建redis连接对象
redis_store = None


# 工厂模式
def create_app(config_name):
    app = Flask(__name__)
    # 根据配置模式的名字获取配置参数的类
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 使用app初始化db
    db.init_app(app)

    # 初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT,
                                    password=config_class.REDIS_PASSWORD, db=2, decode_responses=True)

    # 注册蓝图
    from Notice import admin, user
    app.register_blueprint(user.user, url_prefix="/user")
    app.register_blueprint(admin.admin, url_prefix="/admin")

    return app
