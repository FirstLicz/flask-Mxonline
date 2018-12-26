from flask import render_template, redirect, url_for, make_response, session, request, Response
from flask_login import login_user, logout_user, current_user, login_required
from flask import current_app

from . import courses
from ..models import Course, Lesson, Video, db, UserFavorite


@courses.route('/list/')
def course_list():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'new', type=str)
    if sort == 'new':
        pagination = Course.query.order_by(Course.add_time.desc()).paginate(page, per_page=12, error_out=False)
    elif sort == 'hot':
        pagination = Course.query.order_by(Course.click_nums.desc()).paginate(page, per_page=12, error_out=False)
    elif sort == 'join':
        pagination = Course.query.order_by(Course.students.desc()).paginate(page, per_page=12, error_out=False)
    else:
        pagination = Course.query.order_by(Course.add_time.desc()).paginate(page, per_page=12, error_out=False)
    recommend_course = Course.query.order_by(Course.click_nums.desc()).filter_by(recommend=True)
    if recommend_course:
        recommend_course = recommend_course[:3]
    return render_template(
        'course/course-list.html',
        pagination=pagination,
        sort=sort,
        recommend_course=recommend_course
    )


@courses.route('/detail/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(int(course_id))
    if not current_user.is_anonymous:
        current_user.courses.append(course)
        db.session.add(current_user)
        db.session.commit()
    if current_user.is_anonymous:
        course_has_fav = False
        org_has_fav = False
    else:
        course_has_fav = UserFavorite.query.filter_by(fav_type=0, fav_id=course.id, user_id=current_user.id).first()
        org_has_fav = UserFavorite.query.filter_by(fav_type=1, fav_id=course.courseorg_id, user_id=current_user.id).first()
    # 相关课程推荐
    # recommend_courses = Course.query.filter_by(recommend=True,)
    return render_template(
        'course/course-detail.html',
        course=course,
        course_has_fav=course_has_fav,
        org_has_fav=org_has_fav,
    )


@courses.route('/section/<int:course_id>')
@login_required
def course_section(course_id):
    course = Course.query.get_or_404(int(course_id))
    return render_template(
        'course/course-video.html',
        course=course,
    )


@courses.route('/section/<int:course_id>/video/<int:video_id>')
@login_required
def course_video(course_id, video_id):
    course = Course.query.get_or_404(int(course_id))
    videos = Video.query.get_or_404(int(video_id))
    return render_template(
        'course/course-play.html',
        videos=videos,
        course=course,
    )
