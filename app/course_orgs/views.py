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
    return render_template(
        'org/org-list.html',
        pagination=pagination,
        org_type=CourseOrg.ORG_CATEGORY,
        category=category,
        cities=cities,
        city_id=city_id,
    )
