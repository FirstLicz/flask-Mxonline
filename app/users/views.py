from flask import render_template, redirect, url_for, make_response, session, request, Response, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from flask import current_app
from werkzeug.utils import secure_filename
import os

from . import users
from ..models import User, Course, UserFavorite, Teacher, CourseOrg, db, EmailVerifyCode
from ..utils.utils import Pagination, random_verify_code
from .forms import UserInfoForm, UpdateEmailForm, UpdatePassword, UpdateHeadIcon
from ..email import send_verify_code
from config import basedir

static_dir = os.path.join(basedir, 'app', 'static')


@users.route('/info/', methods=['GET', 'POST'])
@login_required
def user_info():
    form = UserInfoForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            response = make_response(jsonify({"status": "success"}))
            form.save()
        else:
            response = make_response(jsonify({"status": "failure", "msg": form.errors}))
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    return render_template(
        'users/usercenter-info.html',
    )


@users.route('/courses/')
@login_required
def user_courses():
    page = request.args.get('page', 1, type=int)
    total_courses = current_user.courses
    pagination = Pagination(page=page, per_page=8, items=total_courses)
    return render_template(
        'users/usercenter-mycourse.html',
        pagination=pagination,
    )


@users.route('/collects/orgs/')
@login_required
def user_collects_orgs():  # 我收藏的机构
    """
        ('1', '机构'),
    """
    page = request.args.get('page', 1, type=int)
    user_favorites = UserFavorite.query.filter_by(fav_type=1, user_id=current_user.id)
    fav_list = []
    if user_favorites:
        for elem in user_favorites:
            query_object = CourseOrg.query.get_or_404(elem.fav_id)
            fav_list.append(query_object)
    pagination = Pagination(page=page, per_page=6, items=fav_list)
    return render_template(
        'users/usercenter-fav-org.html',
        pagination=pagination,
    )


@users.route('/collects/teachers/')
@login_required
def user_collects_teachers():  # 我收藏的讲师
    """
        ('2', '讲师'),
    """
    page = request.args.get('page', 1, type=int)
    user_favorites = UserFavorite.query.filter_by(fav_type=2, user_id=current_user.id)
    fav_list = []
    if user_favorites:
        for elem in user_favorites:
            query_object = Teacher.query.get_or_404(elem.fav_id)
            fav_list.append(query_object)
    pagination = Pagination(page=page, per_page=6, items=fav_list)
    return render_template(
        'users/usercenter-fav-teacher.html',
        pagination=pagination,
    )


@users.route('/collects/courses/')
@login_required
def user_collects_courses():  # 我收藏的课程
    """ ('0', '课程'),
    """
    page = request.args.get('page', 1, type=int)
    user_favorites = UserFavorite.query.filter_by(fav_type=0, user_id=current_user.id)
    fav_list = []
    if user_favorites:
        for elem in user_favorites:
            query_object = Course.query.get_or_404(elem.fav_id)
            fav_list.append(query_object)
    pagination = Pagination(page=page, per_page=6, items=fav_list)
    return render_template(
        'users/usercenter-fav-course.html',
        pagination=pagination,
    )


@users.route('/messages/')
@login_required
def user_messages():
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages
    pagination = Pagination(page=page, per_page=8, items=messages)
    for message in pagination.get_items:
        message.has_read = True
        db.session.add(message)
    db.session.commit()
    return render_template(
        'users/usercenter-message.html',
        pagination=pagination,
    )


@users.route('/add_collect/', methods=['POST', ])
@login_required
def add_user_collect():
    """
        ('0', '课程'),
        ('1', '机构'),
        ('2', '讲师'),
    """
    if request.method == 'POST':
        if not current_user.is_authenticated:
            response = make_response(jsonify({"status": "failed", "msg": "用户未登录"}))
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        fav_id = request.values.get('fav_id')
        fav_type = request.values.get('fav_type')
        fav_record = UserFavorite.query.filter_by(fav_type=fav_type, fav_id=fav_id).first()
        if fav_record:
            db.session.delete(fav_record)
            # 计算收藏数量
            response = make_response(jsonify({"status": "success", "msg": "收藏"}))
            if int(fav_type) == 0:
                fav_object = Course.query.get_or_404(fav_id)
                fav_object.fav_nums -= 1
            elif int(fav_type) == 1:
                fav_object = CourseOrg.query.get_or_404(fav_id)
                fav_object.fav_nums -= 1
            elif int(fav_type) == 2:
                fav_object = Teacher.query.get_or_404(fav_id)
                fav_object.fav_nums -= 1
            db.session.add(fav_object)
        else:
            user_fav = UserFavorite(fav_id=fav_id, fav_type=fav_type, user_id=current_user.id)
            db.session.add(user_fav)
            if int(fav_type) == 0:
                fav_object = Course.query.get_or_404(fav_id)
                fav_object.fav_nums += 1
            elif int(fav_type) == 1:
                fav_object = CourseOrg.query.get_or_404(fav_id)
                fav_object.fav_nums += 1
            elif int(fav_type) == 2:
                fav_object = Teacher.query.get_or_404(fav_id)
                fav_object.fav_nums += 1
            db.session.add(fav_object)
            response = make_response(jsonify({"status": "success", "msg": "已收藏"}))
        db.session.commit()
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@users.route('/update_head_icon/', methods=['POST'])
@login_required
def update_head_icon():
    form = UpdateHeadIcon()
    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        upload_dir = os.path.join(static_dir, 'media/uploadFile/user', str(current_user.id))
        print(upload_dir)
        if not os.path.isdir(upload_dir):
            os.makedirs(upload_dir)
        f.save(os.path.join(upload_dir, filename))
        current_user.image = 'media/uploadFile/user' + '/' + str(current_user.id) + '/' + filename
        db.session.add(current_user)
        db.session.commit()
        response = make_response(jsonify({"status": "success"}))
    else:
        response = make_response(jsonify({"status": "failed", "msg": form.errors.get('image')}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@users.route('/update_password/', methods=['POST'])
@login_required
def update_user_password():
    form = UpdatePassword()
    if form.validate_on_submit():
        form.save()
        response = make_response(jsonify({"status": "success"}))
    else:
        response = make_response(jsonify({"status": "failed", "msg": form.errors.get('password1')}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@users.route('/update_email/', methods=['POST'])
@login_required
def update_user_email():
    form = UpdateEmailForm()
    if form.validate_on_submit():
        form.save()
        response = make_response(jsonify({"status": "success", "msg": "已收藏"}))
    else:
        response = make_response(jsonify({"email": form.errors}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@users.route('/send_email_code/')
@login_required
def send_email_code():
    email = request.args.get('email', type=str)
    if email is None:
        response = make_response(jsonify({'email': '邮箱不能为空'}))
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    result = User.query.filter_by(email=email).first()
    if result:
        response = make_response(jsonify({'email': '邮箱已存在'}))
    else:
        templates = dict()
        code = random_verify_code()
        templates['code'] = code
        templates['username'] = current_user.username
        send_verify_code(email, '修改邮箱', templates, send_type='update_email')
        record = EmailVerifyCode()
        record.email = email
        record.code = code
        record.code_type = '2'
        db.session.add(record)
        db.session.commit()
        response = make_response(jsonify({'status': 'success'}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
