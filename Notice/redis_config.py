import functools

import redis
from flask import request, jsonify, g, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


REDIS = redis.Redis(host='47.107.37.25', port=6379, password="sohei", db=0, decode_responses=True)
REDIS.setnx("notice", 0)
REDIS.setnx("upload", 0)
REDIS.setnx("get_notice", 0)
REDIS.setnx("get_notice_all", 0)
REDIS.setnx("delete_notice", 0)

# def stop_push_again(view_func):
#     @functools.wraps(view_func)
#     def wrapper(*args, **kwargs):
#         try:
#             token = request.args.get('token', default=0, type=str)
#         except Exception as e1:
#             return jsonify(code=4001, msg='缺少参数token')
#
#         s = Serializer(current_app.config["SECRET_KEY"])
#         try:
#             data = s.loads(token)
#             g.user_id = data['id']
#             print(1)
#             print(g.user_id)
#             print(REDIS.get(data['id']))
#             if g.user_id == REDIS.get(data['id']):
#                 return jsonify(code=400, msg="请求频繁，请稍后再试")
#             REDIS.set(data['id'], data['id'], 10)
#         except Exception as e2:
#             return jsonify(code=4000, msg="登录已过期")
#         return view_func(*args, **kwargs)
#
#     return wrapper