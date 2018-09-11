from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_admin.form import ImageUploadField, thumbgen_filename, Select2Field
from sqlalchemy.event import listens_for
from flask import url_for, request, redirect, abort
from flask_login import current_user
from jinja2 import Markup
import os

file_path = os.path.join(os.path.dirname(__file__), 'static')


class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if current_user.is_anonymous or not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return super(MyAdminIndexView, self).index()


class MyBaseModelView(ModelView):

    # 增加这个必须要登录后才能访问，不然显示403错误
    # 但是还是不许再每一个函数前加上这么判定的  ，不然还是可以直接通过地址访问
    def is_accessible(self):
        if not current_user.is_authenticated:
            abort(403)
        if not current_user.role.name == 'Administrator':
            abort(403)
        return True

    # 跳转
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


    def _list_thumbnail(view, context, model, name):
        if not model.image:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename=thumbgen_filename(model.image)))

    column_formatters = {
        'image': _list_thumbnail
    }


class UserModelView(MyBaseModelView):
    def on_model_change(self, form, User, is_created=False):
        # 调用用户模型中定义的set方法
        User.set_password(form.password_hash.data)

    column_exclude_list = ['password_hash', ]
    # column_editable_list = ['name', 'last_name']
    form_excluded_columns = ['messages', 'comments', 'password_hash']
    from .models import User
    column_choices = {
        'gender': User.GENDER,
    }

    form_overrides = dict(
        gender=Select2Field,
    )
    form_args = dict(
        gender=dict(coerce=str, choices=User.GENDER),
    )

    form_extra_fields = {
        'image': ImageUploadField(
            'Image',
            base_path=file_path,
            relative_path='media/uploadFile/',
            thumbnail_size=(60, 60, True)),

    }


class TeacherModelView(MyBaseModelView):
    from .models import Teacher
    column_choices = {
        'profession': Teacher.PROFESSIONAL,
    }
    form_overrides = dict(
        profession=Select2Field,
    )
    form_args = dict(
        profession=dict(coerce=str, choices=Teacher.PROFESSIONAL),
    )
    form_extra_fields = {
        'image': ImageUploadField(
            'Image',
            base_path=file_path,
            relative_path='media/uploadFile/',
            thumbnail_size=(60, 60, True)),

    }


class CityModelView(MyBaseModelView):
    form_excluded_columns = ['courseorgs', ]


class UserFavoriteModelView(MyBaseModelView):
    from .models import UserFavorite
    column_choices = {
        'fav_type': UserFavorite.FAV_TYPES,
    }

    form_overrides = dict(
        fav_type=Select2Field,
    )
    form_args = dict(
        fav_type=dict(coerce=str, choices=UserFavorite.FAV_TYPES),
    )


class EmailVerifyCodeModelView(MyBaseModelView):
    from .models import EmailVerifyCode
    column_choices = {
        'code_type': EmailVerifyCode.CODE_TYPES,
    }

    form_overrides = dict(
        code_type=Select2Field,
    )
    form_args = dict(
        code_type=dict(coerce=str, choices=EmailVerifyCode.CODE_TYPES),
    )


class BannerModelView(MyBaseModelView):
    form_extra_fields = {
        'image': ImageUploadField(
            'Image',
            base_path=file_path,
            relative_path='media/uploadFile/',
            thumbnail_size=(60, 60, True)),

    }


class CourseModelView(MyBaseModelView):
    from .models import Course
    column_choices = {
        'degree': Course.COURSE_GRADE,
    }

    form_excluded_columns = ['lessions', ]
    form_overrides = dict(
        degree=Select2Field,
    )
    form_args = dict(
        degree=dict(coerce=str, choices=Course.COURSE_GRADE),
    )
    form_extra_fields = {
        'image': ImageUploadField(
            'Image',
            base_path=file_path,
            relative_path='media/uploadFile/',
            thumbnail_size=(60, 60, True)),

    }


class CourseCommentsModelView(MyBaseModelView):
    pass


class CourseResourceModelView(MyBaseModelView):
    pass


class CourseOrgModelView(MyBaseModelView):
    form_excluded_columns = ['courses', 'teachers']


from .models import User, Teacher, Course


# 监听删除图片的
@listens_for(User, 'after_delete')
def del_image(mapper, connection, target):
    if target.image:
        # Delete image
        try:
            os.remove(os.path.join(file_path, target.image))
        except OSError:
            pass
        # Delete thumbnail
        try:
            os.remove(os.path.join(file_path, thumbgen_filename(target.image)))
        except OSError:
            pass


@listens_for(Teacher, 'after_delete')
def del_image(mapper, connection, target):
    if target.image:
        # Delete image
        try:
            os.remove(os.path.join(file_path, target.image))
        except OSError:
            pass
        # Delete thumbnail
        try:
            os.remove(os.path.join(file_path, thumbgen_filename(target.image)))
        except OSError:
            pass


@listens_for(Course, 'after_delete')
def del_image(mapper, connection, target):
    if target.image:
        # Delete image
        try:
            os.remove(os.path.join(file_path, target.image))
        except OSError:
            pass
        # Delete thumbnail
        try:
            os.remove(os.path.join(file_path, thumbgen_filename(target.image)))
        except OSError:
            pass
