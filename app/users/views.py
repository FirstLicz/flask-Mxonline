from flask import render_template, redirect, url_for, make_response, session, request, Response
from flask_login import login_user, logout_user, current_user, login_required
from flask import current_app

from . import users
from ..models import User, Course
from ..utils.utils import Pagination


@users.route('/info/')
@login_required
def user_info():
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


@users.route('/collects/')
@login_required
def user_collects():
    return render_template(
        'users/usercenter-mycourse.html',
    )


@users.route('/messages/')
@login_required
def user_messages():
    return render_template(
        'users/usercenter-mycourse.html',
    )
