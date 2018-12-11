from flask import render_template, redirect, url_for, make_response, session, request, Response
from flask_login import login_user, logout_user, current_user, login_required
from flask import current_app

from . import users
from ..models import User, Course, UserFavorite, Teacher, CourseOrg
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
            query_object = CourseOrg.query.get_or_404(elem)
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
            query_object = Teacher.query.get_or_404(elem)
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
            query_object = Course.query.get_or_404(elem)
            fav_list.append(query_object)
    pagination = Pagination(page=page, per_page=6, items=fav_list)
    return render_template(
        'users/usercenter-fav-course.html',
        pagination=pagination,
    )


@users.route('/messages/')
@login_required
def user_messages():
    return render_template(
        'users/usercenter-mycourse.html',
    )
