from flask import render_template, redirect, url_for, make_response, session, request, Response
from flask_login import login_user, logout_user, current_user, login_required
from flask import current_app

from . import org
from ..models import CourseOrg, CityDict, Course, Teacher, UserFavorite


@org.route('/list/')
def org_list():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('ct', default='')
    city_id = request.args.get('city', default='', type=int)
    cities = CityDict.query.all()
    pagination = CourseOrg.query.paginate(page, per_page=current_app.config['FLASK_PER_PAGE'],
                                          error_out=False)
    if category and city_id:
        pagination = CourseOrg.query.filter_by(category=category, city_id=city_id).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'], error_out=False)
    elif city_id:
        pagination = CourseOrg.query.filter_by(city_id=city_id).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'], error_out=False)
    elif category:
        pagination = CourseOrg.query.filter_by(category=category).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'], error_out=False)

    org_sort = CourseOrg.query.order_by(CourseOrg.students.desc())
    return render_template(
        'org/org-list.html',
        pagination=pagination,
        org_type=CourseOrg.ORG_CATEGORY,
        category=category,
        cities=cities,
        city_id=city_id,
        org_sort=org_sort,
    )


@org.route('/home/<int:org_id>')
def org_home_page(org_id):
    """
        课程机构首页
    :param org_id:  课程机构  ID
    :return:
    """
    organization = CourseOrg.query.get_or_404(int(org_id))
    courses = organization.courses[:4]
    teachers = organization.teachers[:3]
    has_fav = UserFavorite.query.filter_by(fav_type=1, fav_id=organization.id, user_id=current_user.id).first()
    return render_template(
        'org/org-detail-homepage.html',
        organization=organization,
        courses=courses,
        teachers=teachers,
        has_fav=has_fav,
    )


@org.route('/course/<int:org_id>')
def org_course_page(org_id):
    """
        课程机构首页
    :param org_id:  课程机构  ID
    :return:
    """
    organization = CourseOrg.query.get_or_404(int(org_id))
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.filter_by(courseorg=organization).paginate(page, per_page=8, error_out=False)
    return render_template(
        'org/org-detail-course.html',
        organization=organization,
        pagination=pagination,
    )


@org.route('/detail/<int:org_id>')
def org_detail_page(org_id):
    """
        课程机构首页
    :param org_id:  课程机构  ID
    :return:
    """
    organization = CourseOrg.query.get_or_404(int(org_id))
    return render_template(
        'org/org-detail-desc.html',
        organization=organization,
    )


@org.route('/teacher/<int:org_id>')
def org_teacher_page(org_id):
    """
        课程机构首页
    :param org_id:  课程机构  ID
    :return:
    """
    organization = CourseOrg.query.get_or_404(int(org_id))
    return render_template(
        'org/org-detail-teachers.html',
        organization=organization,
    )


@org.route('/teacher/list/')
def teacher_list():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'default', type=str)
    pagination = Teacher.query.order_by().paginate(page, per_page=6, error_out=False)
    if sort == 'hot':
        pagination = Teacher.query.order_by(Teacher.hits.desc()).paginate(page, per_page=6, error_out=False)
    total_teachers = Teacher.query.count()
    ranking_teachers = Teacher.query.order_by(Teacher.hits.desc()).filter_by()[:5]
    return render_template(
        'org/teacher-list.html',
        pagination=pagination,
        sort=sort,
        total_teachers=total_teachers,
        ranking_teachers=ranking_teachers,
    )


@org.route('/teacher/detail/<int:teacher_id>')
def teacher_detail(teacher_id):
    page = request.args.get('page', 1, type=int)
    teacher = Teacher.query.get_or_404(teacher_id)
    pagination = Course.query.filter_by(teacher_id=teacher_id).paginate(page, per_page=8, error_out=False)
    course_org = CourseOrg.query.get_or_404(teacher.course_org_id)
    org_teachers = Teacher.query.filter_by(course_org_id=teacher.course_org_id).order_by(Teacher.hits.desc())[:5]
    org_has_fav = UserFavorite.query.filter_by(fav_type=1, fav_id=teacher.courseorg.id, user_id=current_user.id).first()
    teacher_has_fav = UserFavorite.query.filter_by(fav_type=2, fav_id=teacher.id, user_id=current_user.id).first()
    return render_template(
        'org/teacher-detail.html',
        teacher=teacher,
        pagination=pagination,
        course_org=course_org,
        org_teachers=org_teachers,
        org_has_fav=org_has_fav,
        teacher_has_fav=teacher_has_fav,
    )
