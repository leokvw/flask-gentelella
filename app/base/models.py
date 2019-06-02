from bcrypt import gensalt, hashpw
from flask_login import UserMixin
from sqlalchemy import VARBINARY, Column, Integer, String, Boolean, TIMESTAMP, BIGINT, SmallInteger, ForeignKey, \
    PickleType

from app import db, login_manager


class Admin(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    password = Column(VARBINARY)
    create = Column(TIMESTAMP)

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


class Building(db.Model):
    __table_args__ = {'extend_existing': True}

    number = Column(SmallInteger, primary_key=True)
    name = Column(String(20), nullable=False)

    def __repr__(self):
        return '<Building {}>'.format(self.number)


class Resident(db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    name = Column(String(20), nullable=False)
    mobile = Column(String(20), nullable=False)
    password = Column(String(32), server_default='123456')
    building = Column(SmallInteger, ForeignKey(Building.number))
    face_encoding = Column(PickleType)
    create = Column(TIMESTAMP)

class Visitor(db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    is_expire = Column(Boolean, nullable=False)
    building = Column(SmallInteger, ForeignKey(Building.number))
    create = Column(TIMESTAMP)


class Capture(db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    on_record = Column(Boolean, nullable=False)
    building = Column(SmallInteger, ForeignKey(Building.number))
    create = Column(TIMESTAMP)


class Access(db.Model):
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, autoincrement=True, primary_key=True)
    direction = Column(Boolean, server_default='0')
    type = Column(SmallInteger, server_default='0')
    name = Column(String(20), nullable=True)
    building = Column(SmallInteger, ForeignKey(Building.number))
    create = Column(TIMESTAMP)


@login_manager.user_loader
def user_loader(id):
    return Admin.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    name = request.form.get('name')
    admin = Admin.query.filter_by(name=name).first()
    return admin if admin else None
