from flask import render_template, redirect, url_for, make_response, session, request, Response
from flask_login import login_user, logout_user, current_user, login_required
from io import BytesIO
from flask import current_app

from . import org
from ..models import CourseOrg, CityDict


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
    if city_id:
        pagination = CourseOrg.query.filter_by(city_id=city_id).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'], error_out=False)
    if category:
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
    print(dir(org_home_page))
    return render_template(
        'org/org-detail-homepage.html',
        organization=organization,
        courses=courses,
        teachers=teachers,
    )
