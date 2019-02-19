from flask import render_template, redirect, url_for, request, session, abort
from flask_login import current_user
from io import BytesIO

from . import index
from ..models import Banner, CourseOrg, Course


@index.route('/')
def index():
    banners = Banner.query.order_by(Banner.add_time.desc()).filter_by()[:5]
    banner_courses = Course.query.order_by(Course.add_time.desc()).filter_by(is_banner=True)[:3]
    courses = Course.query.order_by(Course.add_time.desc()).filter_by()[:6]
    orgs = CourseOrg.query.order_by(CourseOrg.add_time.desc()).filter_by()[:15]
    return render_template(
        'index/index.html',
        banners=banners,
        banner_courses=banner_courses,
        courses=courses,
        orgs=orgs,
    )
