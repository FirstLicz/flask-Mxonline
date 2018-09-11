from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, ValidationError, Length, EqualTo
from wtforms import StringField, SubmitField, PasswordField
from flask import session

from app.models import User
from app import db


class LoginForm(FlaskForm):
    username = StringField('用户邮箱', validators=[DataRequired()], render_kw={"placeholder": "用户名/邮箱",
                                                                           "id": "account_l"})
    password = PasswordField('密码', validators=[DataRequired()], render_kw={"placeholder": "请输入您的密码",
                                                                           "id": "password_l"})
    submit = SubmitField('立即登录', render_kw={"class": "btn btn-green", "id": "jsLoginBtn"})

    def validate_username(self, field):
        result = self.get_user()
        if not result:
            raise ValidationError('用户或邮箱不存在')

    def get_user(self):
        ret1 = User.query.filter_by(username=self.username.data).first()
        ret2 = User.query.filter_by(email=self.username.data).first()
        if ret1 or ret2:
            return ret1 or ret2
        else:
            return None


class RegisterForm(FlaskForm):
    """
        用户注册功能
    """
    email = StringField('邮箱', validators=[DataRequired(), Email()], render_kw={"placeholder": "请输入您的邮箱地址",
                                                                               "id": "id_email"})
    password = PasswordField('密码', validators=[DataRequired()], render_kw={"placeholder": "请输入6-20位非中文字符密码",
                                                                           "id": "id_password"})
    captcha = StringField('验证码', validators=[DataRequired(), Length(4, 4, message='验证码必填')], render_kw={
        "autocomplete": "off", "id": "id_captcha_1"})
    submit = SubmitField('注册', render_kw={"class": "btn btn-green", "id": "jsEmailRegBtn"})

    def validate_email(self, field):
        result = self.get_user()
        if result:
            raise ValidationError('邮箱已存在')

    def validate_captcha(self, field):
        code = session.get('code_text', None)
        if code.lower() != field.data.lower():
            raise ValidationError('验证不正确')

    def get_user(self):
        result = User.query.filter_by(email=self.email.data).first()
        return result

    def save(self):
        u = User()
        u.username = self.email.data
        u.email = self.email.data
        u.password = self.password.data
        u.role.name = 'User'
        db.session.add(u)
        db.session.commit()


class ForgetPasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()], render_kw={"placeholder": "邮箱",
                                                                               "id": "account"})
    captcha = StringField('验证码', validators=[DataRequired(), Length(4, 4, message='验证码必填')], render_kw={
        "autocomplete": "off", "id": "id_captcha_1"})

    submit = SubmitField('提交', render_kw={"class": "btn btn-green", "id": "jsFindPwdBtn"})

    def validate_email(self, field):
        result = self.get_user()
        if not result:
            raise ValidationError('邮箱不存在')

    def get_user(self):
        result = User.query.filter_by(email=self.email.data).first()
        return result

    def validate_captcha(self, field):
        code = session.get('code_text', None)
        if code.lower() != field.data.lower():
            raise ValidationError('验证不正确')


class ModifyPasswordForm(FlaskForm):
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 20)],
                             render_kw={"placeholder": "6-20位非中文字符", "id": "pwd"})
    password_again = PasswordField(
        '密码',
        validators=[DataRequired(), Length(6, 20), EqualTo('password', message='两次输入不一致')],
        render_kw={"placeholder": "6-20位非中文字符", "id": "repwd"})
    submit = SubmitField('提交')

