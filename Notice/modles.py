from . import db
from datetime import datetime


class Photo(db.Model):
    __tablename__ = "photo"
    id = db.Column(db.Integer, primary_key=True)  # id号(独一无二的)
    photo = db.Column(db.String(64))     # 图片
    notice_id = db.Column(db.Integer, db.ForeignKey('notice.id'))
    create_time = db.Column(db.DateTime, default=datetime.now)


class Notice(db.Model):
    __tablename__ = "notice"
    id = db.Column(db.Integer, primary_key=True)  # id号(独一无二的)
    status = db.Column(db.Enum("寻物启事", "物品招领"), default="寻物启事", nullable=False)
    location = db.Column(db.String(16), nullable=False)     # 地点
    text = db.Column(db.TEXT, nullable=False)  # 内容
    phone = db.Column(db.String(32), nullable=False)  # 手机号
    wechat = db.Column(db.String(32), nullable=False)       # 微信号
    user_photo = db.relationship('Photo', backref='notice')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_time = db.Column(db.DateTime, default=datetime.now)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    username = db.Column(db.String(128), unique=True)  # 用户名　（唯一的）
    password = db.Column(db.String(128))
    user_notice = db.relationship('Notice', backref='user')


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    username = db.Column(db.String(128), unique=True)  # 管理员用户名　（唯一的）
    password = db.Column(db.String(128))  # 管理员密码


if __name__ == '__main__':
    db.create_all()
