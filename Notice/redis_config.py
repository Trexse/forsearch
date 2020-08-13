import functools
from flask import request, jsonify, g, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import redis

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
r = redis.Redis(connection_pool=pool)
r.flushall()


def stop_push_again(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            token = request.args.get('token', default=0, type=str)
        except Exception as e1:
            return jsonify(code=4001, msg='缺少参数token')

        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
            g.user_id = data['id']
            if g.user_id == r.get(data['id']):
                return jsonify(code=400, msg="请求频繁，请稍后再试")
            r.set(data['id'], data['id'], 10)
        except Exception as e2:
            return jsonify(code=4000, msg="登录已过期")
        return view_func(*args, **kwargs)

    return wrapper