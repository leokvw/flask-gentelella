from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, IntegerField, SubmitField, FileField

from wtforms.validators import DataRequired

from app import resident_images, capture_images


class LoginForm(FlaskForm):
    id = IntegerField('工号', id='id_login')
    password = PasswordField('密码', id='pwd_login')


class CreateAccountForm(FlaskForm):
    name = StringField('用户名', id='username_create')
    password = PasswordField('密码', id='pwd_create')


class BuildingForm(FlaskForm):
    number = IntegerField('楼号', validators=[DataRequired()])
    name = StringField('楼名', validators=[DataRequired()])

    submit_button = SubmitField('提交')


class ResidentForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired()])
    mobile = StringField('手机号', validators=[DataRequired()])
    portrait = FileField('头像', validators=[
        FileRequired(message='您还没有选择文件'),
        FileAllowed(resident_images,message='只能上传图片')])
    password = PasswordField('密码')
    building = IntegerField('楼号')

    submit_button = SubmitField('提交')


class VisitorForm(FlaskForm):
    name = StringField('名字', validators=[DataRequired()])
    building = IntegerField('目标住宅', validators=[DataRequired()])

    submit_button = SubmitField('提交')
