from app import db
from app.base.models import User


def init():
    return db.session.query(User)
