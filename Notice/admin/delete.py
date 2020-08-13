import functools
from urllib import request

from flask import jsonify, current_app, g
from itsdangerous import Serializer

from . import admin
from .. import db
from ..modles import Notice, Photo
from ..redis_config import r


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
    print("notice使用次数:"+r.get("notice")/"使用人数:"+r.scard("notice"))
    print("upload使用次数:" + r.get("upload") / "使用人数:" + r.scard("upload"))
    print("get_notice使用次数:" + r.get("get_notice") / "使用人数:" + r.scard("get_notice"))
    print("get_notice_all使用次数:" + r.get("get_notice_all") / "使用人数:" + r.scard("get_notice_all"))
    print("delete_notice使用次数:" + r.get("delete_notice") / "使用人数:" + r.scard("delete_notice"))