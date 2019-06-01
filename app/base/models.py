from bcrypt import gensalt, hashpw
from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String, Boolean
from safrs import SAFRSBase

from app import db, login_manager


class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            if property == 'password':
                value = hashpw(value.encode('utf8'), gensalt())
            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


class Building(db.Model):
    __table_args__ = {'extend_existing': True}

    number = Column(Integer, primary_key=True)

    def __repr__(self):
        return '<Building {}>'.format(self.number)


class Resident(db.Model, SAFRSBase):
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    mobile = Column(String, nullable=False)
    portrait = Column(String, server_default='undefined_portrait.png')
    password = Column(String, server_default='123456')
    number = Column(Integer)

    def __init__(self, id, name, mobile, number):
        self.id = id
        self.name = name
        self.mobile = mobile
        self.number = number


class Visitor(SAFRSBase, db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, autoincrement=True, primary_key=True)


class Capture(SAFRSBase, db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, autoincrement=True, primary_key=True)
    # 采集到的人脸图像是否符合数据库中原有的人脸数据,0-不符合,1-符合
    on_record = Column(Boolean, nullable=False)
    building = Column(Integer, nullable=False)


class Access(db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    # 进出方向,0-进入,1-出门,默认进门
    direction = Column(Boolean, server_default='0')
    # '0-住户,1-访客,默认住户进出',
    type = Column(Boolean, server_default='0')


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None
