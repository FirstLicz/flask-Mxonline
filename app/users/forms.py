from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, ValidationError, Length, EqualTo
from wtforms import StringField, SubmitField, PasswordField, BooleanField, DateField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from datetime import datetime, timedelta

from app.models import User, EmailVerifyCode
from app import db


class UserInfoForm(FlaskForm):
    nick_name = StringField('用户名', validators=[DataRequired()], render_kw={"placeholder": "用户名"})
    address = StringField('用户地址', validators=[], render_kw={"placeholder": "请输入你的地址"})
    email = StringField('用户邮箱', validators=[Email()], )
    mobile = StringField('手机号码', validators=[DataRequired()], )
    gender = BooleanField('性别', validators=[DataRequired()], )
    birthday = DateField('生日日期', validators=[DataRequired()], )
    submit = SubmitField('保存')

    def validate_nick_name(self, field):
        result = self.get_user()
        if result is False:
            raise ValidationError('用户已存在')

    def get_user(self):
        ret1 = User.query.filter(User.id.notin_([current_user.id, ])).filter_by(username=self.nick_name.data).first()
        if ret1:
            return False
        else:
            return True

    def save(self):
        current_user.username = self.nick_name.data
        current_user.address = self.address.data
        current_user.email = self.email.data
        current_user.gender = self.gender.data
        current_user.birthday = self.birthday.data
        current_user.mobile = self.mobile.data
        db.session.add(current_user)
        db.session.commit()


class UpdateEmailForm(FlaskForm):
    email = StringField('用户邮箱', validators=[Email()], )
    code = StringField('邮箱验证码', validators=[DataRequired()], )
    submit = SubmitField('submit')

    def validate_email(self, field):
        result = self.get_user()
        if result is False:
            raise ValidationError('邮箱已存在')

    def get_user(self):
        ret = User.query.filter_by(email=self.email.data).first()
        if ret:
            return False
        else:
            return True

    def save(self):  # 当前时间前60秒内的验证码有效
        verify_code = EmailVerifyCode.query.filter(EmailVerifyCode.add_time >=
                                                   (datetime.now() - timedelta(seconds=60))) \
            .filter_by(code_type='2', code=self.code.data, email=self.email.data, ).first()
        if verify_code:
            current_user.email = self.email.data
            db.session.add(current_user)
            db.session.commit()


class UpdatePassword(FlaskForm):
    password1 = PasswordField('新密码', validators=[DataRequired(), EqualTo('password2', "两次密码不一致")])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])

    def save(self):
        current_user.password = self.password1.data
        db.session.add(current_user)
        db.session.commit()


class UpdateHeadIcon(FlaskForm):
    image = FileField('头像', validators=[FileRequired()])

