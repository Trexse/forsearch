# 默认配置信息
import os

# 默认的管理员 账号和密码还有头像
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "666"

# Mysql数据库信息配置
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'whatever-guess'
WTF_CSRF_ENABLED = False

# Redis配置信息
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = 6379
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

# flask-session配置
PERMANENT_SESSION_LIFETIME = 3600  # 86400 session数据的有效期，单位秒