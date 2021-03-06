from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_babelex import Babel
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect

from config import config
from .template_filters import do_format_date, do_slicer, diff_time_year

db = SQLAlchemy()
mail = Mail()
bootstrap = Bootstrap()
admin = Admin(template_mode='bootstrap3', name='在线教育系统后台')
babel = Babel()
editor = CKEditor()
login_manager = LoginManager()
csrf_protect = CSRFProtect()

login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

from app.models import User, Course, Teacher, CourseOrg, CityDict, UserFavorite, EmailVerifyCode, \
    Banner, CourseComments, CourseResource, Video, Lesson
from .xadmin import UserModelView, CityModelView, CourseModelView, TeacherModelView, \
    UserFavoriteModelView, EmailVerifyCodeModelView, BannerModelView, CourseCommentsModelView, \
    CourseResourceModelView, CourseOrgModelView, VideoModelView, LessonModelView

admin.add_view(UserModelView(User, db.session, name='用户'))
admin.add_view(CityModelView(CityDict, db.session, name='城市'))
admin.add_view(CourseModelView(Course, db.session, name='课程'))
admin.add_view(LessonModelView(Lesson, db.session, name='章节'))
admin.add_view(VideoModelView(Video, db.session, name='章节视频'))
admin.add_view(CourseOrgModelView(CourseOrg, db.session, name='授课机构'))
admin.add_view(CourseCommentsModelView(CourseComments, db.session, name='课程评论'))
admin.add_view(CourseResourceModelView(CourseResource, db.session, name='课程资源'))
admin.add_view(TeacherModelView(Teacher, db.session, name='讲师'))
admin.add_view(UserFavoriteModelView(UserFavorite, db.session, name='用户收藏'))
admin.add_view(EmailVerifyCodeModelView(EmailVerifyCode, db.session, name='邮箱验证码'))
admin.add_view(BannerModelView(Banner, db.session, name='首页轮播图'))


def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
    )


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from .xadmin import MyAdminIndexView  # 修改admin 默认view

    db.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    admin.init_app(app, index_view=MyAdminIndexView())
    babel.init_app(app)
    editor.init_app(app)
    login_manager.init_app(app)
    csrf_protect.init_app(app)

    app.add_template_filter(do_format_date, 'datetime')  # 注册到app模板过滤器
    app.add_template_filter(do_slicer, 'slicer')  # 注册到app模板过滤器
    app.add_template_filter(diff_time_year, 'age_year')  # 注册到app模板过滤器

    from .index import index as index_blueprint
    app.register_blueprint(index_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .course import courses as course_blueprint
    app.register_blueprint(course_blueprint, url_prefix='/course')

    from .course_orgs import org as org_blueprint
    app.register_blueprint(org_blueprint, url_prefix='/org')

    from .users import users as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
