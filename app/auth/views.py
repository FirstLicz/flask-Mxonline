from flask import render_template, redirect, url_for, make_response, session, request, Response
from flask_login import login_user, logout_user, current_user, login_required
from io import BytesIO

from .forms import LoginForm, RegisterForm, ForgetPasswordForm, ModifyPasswordForm
from . import auth
from ..models import User, UserMessage
from ..utils.captcha import CaptchaImage
from app import db
from ..email import send_email


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.get_user()
        if not user.verify_password(form.password.data):
            msg = "账号或密码错误"
        else:
            login_user(user)
            user.update_login_time()
            return redirect(url_for("index.index"))
        return render_template('auth/login.html', form=form, msg=msg)
    return render_template('auth/login.html', form=form)


@auth.route('/logout/')
@login_required
def logout():
    current_user.update_logout_time()
    logout_user()
    return redirect(url_for('index.index'))


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        form.save()
        # 注册成功向该邮箱发送激活链接
        user = form.get_user()
        token = user.generate_confirm_token()
        templates = dict()
        templates['url'] = url_for('auth.confirmed', token_id=token, _external=True)
        templates['username'] = user.username
        send_email(user.email, '注册账号', templates)
        user_message = UserMessage(user_id=user.id, message="注册成功，欢迎加入教学网")
        db.session.add(user_message)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.before_app_request  # 全文钩子，在请求之前先预处理
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/confirm/<token_id>')
@login_required
def confirmed(token_id):
    if current_user.confirmed:  # 如果本身已确认，直接跳首页
        return redirect(url_for('index.index'))
    if current_user.confirm(token_id):  # 没有确认，调用确认，没有过期确认通过
        pass
    else:
        return Response('验证链接已过期')
    return redirect(url_for('index.index'))


@auth.route('/unconfirmed/')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('index.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirm():
    # 发送邮件
    token = current_user.generate_confirm_token()
    templates = dict()
    templates['url'] = url_for('auth.confirmed', token_id=token, _external=True)
    templates['username'] = current_user.username
    send_email(current_user.email, '注册账号', templates)
    return render_template('auth/unconfirmed.html')


@auth.route('/forget/', methods=['GET', 'POST'])
def forget_password():
    """
    忘记密码，找回
    """
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = form.get_user()
        token = user.generate_forget_password_token()
        templates = dict()
        templates['url'] = url_for('auth.reset_password', token_id=token, _external=True)
        templates['username'] = user.username
        send_email(user.email, '注册账号', templates)
    return render_template('auth/forgetpwd.html', form=form)


@auth.route('/forget/<token_id>', methods=['GET', 'POST'])
def reset_password(token_id):
    email = User.forget_password(token_id)
    print(email)
    if not email:
        # 过期
        return Response('链接已过期')
    form = ModifyPasswordForm()
    flag = False
    if form.validate_on_submit():
        u = User.query.filter_by(email=email).first()
        print(u)
        u.password = form.password.data
        db.session.add(u)
        db.session.commit()
        flag = True
        user_message = UserMessage(user_id=u.id, message="密码重置成功")
        db.session.add(user_message)
        db.session.commit()
    return render_template('auth/password_reset.html', form=form, token=token_id, flag=flag)


@auth.route('/captcha/')
def captcha():
    image = CaptchaImage()
    img, str_code = image.generate_code_image()
    buf = BytesIO()
    img.save(buf, 'png')
    buf_str = buf.getvalue()
    response = make_response(buf_str)
    session['code_text'] = str_code
    response.headers['Content-Type'] = 'image/gif'
    return response
