from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField

from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('用户名', id='username_login')
    password = PasswordField('密码', id='pwd_login')


class CreateAccountForm(FlaskForm):
    username = StringField('用户名', id='username_create')
    email = StringField('邮箱')
    password = PasswordField('密码', id='pwd_create')


class BuildingForm(FlaskForm):
    id = IntegerField('楼号', validators=[DataRequired()])

    submit_button = SubmitField('提交')


class ResidentForm(FlaskForm):
    id = StringField('身份证号', validators=[DataRequired()])
    name = StringField('姓名', validators=[DataRequired()])
    mobile = StringField('手机号', validators=[DataRequired()])
    portrait = StringField('头像')
    password = PasswordField('密码')
    number = IntegerField('楼号')

    submit_button = SubmitField('提交')


class VisitorForm(FlaskForm):
    id = StringField('序号', validators=[DataRequired()])

    submit_button = SubmitField('提交')


class CaptureForm(FlaskForm):
    id = StringField('序号', validators=[DataRequired()])
    on_record = BooleanField('是否匹配', validators=[DataRequired()])
    building = IntegerField('楼号', validators=[DataRequired()])

    submit_button = SubmitField('提交')


class AccessForm(FlaskForm):
    id = StringField('序号', validators=[DataRequired()])
    direction = BooleanField('进出方向')
    type = BooleanField('是否访客')

    submit_button = SubmitField('提交')
