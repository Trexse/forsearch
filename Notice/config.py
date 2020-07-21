# 需要的配置
import redis
from .message import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY, \
    WTF_CSRF_ENABLED, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


class Config(object):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = SQLALCHEMY_TRACK_MODIFICATIONS
    SECRET_KEY = SECRET_KEY
    WTF_CSRF_ENABLED = WTF_CSRF_ENABLED

    # redis
    REDIS_HOST = REDIS_HOST
    REDIS_PORT = REDIS_PORT
    REDIS_PASSWORD = REDIS_PASSWORD

    # flask-session配置
    SESSION_TYPE = "redis"
    # SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                                      password=REDIS_PASSWORD, db=2)

    SESSION_USE_SIGNER = True  # 对cookie中session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 100  # session数据的有效期，单位秒


class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:jamkung@pukgai.com:3306/caiji_test'
    SESSION_REDIS = redis.Redis(host='pukgai.com', port=6379, password="jamkung", db=2)  # 操作的redis配置
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:jamkung@pukgai.com:3306/caiji_test2'
    SESSION_REDIS = redis.Redis(host='pukgai.com', port=6379, password="jamkung", db=3)
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
