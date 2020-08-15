import functools

from flask import jsonify, current_app, g, request, json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import admin
from .. import db
from ..modles import Notice, Photo, Admin
from ..redis_config import REDIS


def admin_login_token(view_func):
    # wraps函数的作用是将wrapper内层函数的属性设置为被装饰函数view_func的属性
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            token = request.args.get('token', default=0, type=str)
        except Exception as e1:
            return jsonify(code=4001, msg='缺少参数token')

        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
            g.admin_id = data['id']
        except Exception as e2:
            return jsonify(code=4000, msg="登录已过期")
        return view_func(*args, **kwargs)

    return wrapper


@admin.route("/login", methods=["POST"])
def login():
    """用户的登录"""
    # 获取参数
    req_dict = request.get_json()
    username = req_dict.get("username")
    password = req_dict.get("password")

    # 参数完整的校验
    if not all([username, password]):
        return jsonify(code=4001, msg="参数不完整.")

    try:
        admin = Admin.query.filter_by(username=username).first()
    except Exception as e:
        print(e)
        return jsonify(code=4000, msg="获取用户信息失败")

    # 用数据库的密码与用户填写的密码进行对比验证
    if admin is None or admin.password != password:
        return jsonify(code=4000, msg="用户名或密码错误")

    s = Serializer(current_app.config["SECRET_KEY"], expires_in=3600)
    # 接收用户id转换与编码
    token = s.dumps({"id": admin.id}).decode("ascii")
    # 把token返回给前端
    return jsonify(code=200, msg="成功", data=token)


@admin.route("/delete", methods=["DELETE"])
@admin_login_token
def delete_notice():
    admin_id = g.admin_id
    req_dict = request.get_json()
    notice_id = req_dict.get("notice_id")
    if not all([admin_id, notice_id]):
        return jsonify(code=4001, msg="参数不完整")
    try:
        # 删除对应的图片
        r = Photo.query.filter_by(notice_id=notice_id).delete()
        # 删除寻物启事
        t = Notice.query.filter_by(id=notice_id).delete()
        db.session.commit()
        return jsonify(code=200, msg="删除成功")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=4004, msg="删除失败")


@admin.route("/R_O_F", methods=["GET"])
@admin_login_token
def see_rof():
    rof = []
    # print("notice使用次数:"+REDIS.get("notice")/"使用人数:"+REDIS.scard("notice"))
    # print("upload使用次数:" + REDIS.get("upload") / "使用人数:" + REDIS.scard("upload"))
    # print("get_notice使用次数:" + REDIS.get("get_notice") / "使用人数:" + REDIS.scard("get_notice"))
    # print("get_notice_all使用次数:" + REDIS.get("get_notice_all") / "使用人数:" + REDIS.scard("get_notice_all"))
    # print("delete_notice使用次数:" + REDIS.get("delete_notice") / "使用人数:" + REDIS.scard("delete_notice"))
    now_rof = dict(code=200, notice_times=REDIS.get("notice"), notice_people=REDIS.scard("notice2"),
                       upload_times=REDIS.get("upload"), upload_people=REDIS.scard("upload2"),
                       get_notice_times=REDIS.get("get_notice"), get_notice_people=REDIS.scard("get_notice2"),
                       get_notice_all_times=REDIS.get("get_notice_all"), get_notice_all_people=REDIS.scard("get_notice_all2"),
                       delete_notice_times=REDIS.get("delete_notice"), delete_notice_people=REDIS.scard("delete_notice2"))
    rof.append(now_rof)
    print(REDIS.get("notice"))
    resp_json = json.dumps(rof)
    return resp_json, 200, {"Content-Type": "application/json"}