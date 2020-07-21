import functools
import os
import random
import re
from datetime import datetime


from flask import request, jsonify, g, current_app, json
from werkzeug.utils import secure_filename
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from Notice import db
from . import user
from ..modles import User, Notice, Photo


def user_login_token(view_func):
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
            g.user_id = data['id']
        except Exception as e2:
            return jsonify(code=4000, msg="登录已过期")
        return view_func(*args, **kwargs)

    return wrapper


@user.route("/")
def hello_world():
    return "hello"


# 登录
@user.route("/login", methods=["POST"])
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
        user = User.query.filter_by(username=username).first()
    except Exception as e:
        print(e)
        return jsonify(code=4000, msg="获取用户信息失败")

    # 用数据库的密码与用户填写的密码进行对比验证
    if user is None or user.password != password:
        return jsonify(code=4000, msg="用户名或密码错误")

    s = Serializer(current_app.config["SECRET_KEY"], expires_in=3600)
    # 接收用户id转换与编码
    token = s.dumps({"id": user.id}).decode("ascii")
    # 把token返回给前端
    return jsonify(code=200, msg="成功", data=token)


@user.route("/notice", methods=['POST'])
@user_login_token
def notice():
    user_id = g.user_id
    # 获取参数
    req_dict = request.get_json()
    text = req_dict.get("text")
    location = req_dict.get("location")
    phone = req_dict.get("phone")
    wechat = req_dict.get("wechat")
    status = req_dict.get("status")
    if not all([status, text, location, phone, wechat]):
        return jsonify(code=4001, msg="参数不完整")
    if status not in ("寻物启事", "物品招领"):
        return jsonify(code=4001, msg="参数出错")
    else:
        keywords = ("草泥马", "傻逼", "傻吊", "sb", "革命", "党", "习近平", "xjp", "习大大", "xdd")
        text_checked = re.sub("|".join(keywords), "***", text)
        notice = Notice(text=text_checked, location=location, phone=phone, wechat=wechat, status=status, user_id=user_id)
        db.session.add(notice)
        db.session.commit()
        return jsonify(code=200, msg="保存成功，请继续上传图片")


basedir = os.path.abspath(os.path.dirname(__file__))


@user.route("/upload", methods=["POST"])
@user_login_token
def upload():
    notice_id = request.form.get("key", type=str)
    print(notice_id)
    f = request.files.get('file')
    filename = secure_filename(f.filename)
    # 生成随机数
    random_num = random.randint(0, 100)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(random_num) + "." + filename.rsplit('.', 1)[1]
    file_path = basedir + "/static/file/"
    if not os.path.exists(file_path):
        os.makedirs(file_path, 755)
    # 保存文件到目标文件夹
    f.save(file_path + filename)
    # 返回前端可调用的一个链接
    # 可以配置成对应的外网访问的链接
    my_host = "http://127.0.0.1:5000"
    new_path_file = my_host + "/static/file/" + filename
    photo_url = new_path_file
    if not all([photo_url]):
        return jsonify(code=4001, msg="参数不完整")
    photo = Photo(photo=photo_url, notice_id=notice_id)
    try:
        db.session.add(photo)
        db.session.commit()
        return jsonify(code=200, msg="上传图片成功")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=4000, msg="操作数据库失败,请稍后再试")


@user.route("/get_notice", methods=['POST'])
@user_login_token
def get_notice():
    user_id = g.user_id
    req_dict = request.get_json()
    keyword = req_dict.get("keyword")
    if not all([user_id, keyword]):
        return jsonify(code=4001, msg="参数不完整")
    notice_by_keyword = []
    notice_list = Notice.query.filter(Notice.text.like("%" + keyword + "%"))
    for this_notice in notice_list:
        photo = []
        for i in this_notice.user_photo:
            photo.append(i.photo)
        notice_dict = dict(code=200, text=this_notice.text, location=this_notice.location,
                         phone=this_notice.phone, wechat=this_notice.wechat,
                         status=this_notice.status, user_id=this_notice.user_id,
                         this_photo=photo)
        notice_by_keyword.append(notice_dict)
    resp_json = json.dumps(notice_by_keyword)
    return resp_json, 200, {"Content-Type": "application/json"}


@user.route("/get_notice_all", methods=['GET'])
@user_login_token
def get_notice_all():
    notice_id = []
    notice_text = []
    notices = Notice.query.filter_by(status="寻物启事").all()
    for notice in notices:
        notice_id.append(notice.id)
        notice_text.append(notice.text)
    resp_dict = dict(code=200, notice_id=notice_id, notice_text=notice_text)
    resp_json = json.dumps(resp_dict)
    return resp_json, 200, {"Content-Type": "application/json"}


@user.route("/delete_notice", methods=['POST'])
@user_login_token
def delete_notice():
    user_id = g.user_id
    req_dict = request.get_json()
    notice_id = req_dict.get("notice_id")
    this_notice = Notice.query.get(notice_id)
    u_id = this_notice.user_id
    if not all([user_id, notice_id]):
        return jsonify(code=4001, msg="参数不完整")
    if user_id != u_id:
        return jsonify(code=4005, msg="没有权限")
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