from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from sqlalchemy.sql import func

from app import db


# ###### 用户信息  ##########

class Permissions(object):
    CONCERN = 0x01
    COMMENT = 0x02
    WRITE_ARTICLE = 0x04
    MANAGE_COMMENT = 0x08
    ADMINISTRATOR = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(64), index=True, comment='角色', doc='角色')
    permissions = db.Column(db.Integer)
    add_time = db.Column(db.DateTime(), default=datetime.now)
    users = db.relationship('User', backref='role')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permissions.CONCERN | Permissions.COMMENT | Permissions.WRITE_ARTICLE, True),
            'Assist': (Permissions.CONCERN | Permissions.COMMENT |
                       Permissions.WRITE_ARTICLE | Permissions.MANAGE_COMMENT, False),
            'Administrator': (0xff, False)
        }
        for r, permission in roles.items():
            role = Role.query.filter_by(name=r).first()
            if role:
                continue
            role = Role(name=r)
            role.permissions = permission[0]
            role.default = permission[1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role,%s>" % self.name

    def __str__(self):
        return self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    GENDER = (
        ('0', '男'),
        ('1', '女'),
    )
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    username = db.Column(db.String(128), nullable=False, index=True, comment='用户名', doc='用户名')
    name = db.Column(db.String(128), index=True, comment='真名', doc='真名')
    confirmed = db.Column(db.Boolean, default=False, comment='是否确认', doc='是否确认')
    password_hash = db.Column(db.String(256), default='123456', nullable=False, comment='密码密文', doc='密码密文')
    image = db.Column(db.String(128), nullable=True, comment='用户头像', doc='用户头像')
    email = db.Column(db.String(128), nullable=True, index=True, unique=True, comment='邮箱', doc='邮箱')
    gender = db.Column(db.String(1), nullable=True, default='0', comment='性别', doc='性别')
    address = db.Column(db.String(200), nullable=True, comment='用户地址', doc='用户地址')
    mobile = db.Column(db.String(11), nullable=True, comment='手机号码', doc='手机号码')
    birthday = db.Column(db.Date, default=datetime.now().date, comment='生日日期', doc='生日日期')
    add_time = db.Column(db.DateTime(), default=datetime.now, comment='创建时间', doc='创建时间')
    last_login = db.Column(db.DateTime(), comment='最后一次登录时间', doc='最后一次登录时间')
    last_logout = db.Column(db.DateTime(), comment='最后一次退出时间', doc='最后一次退出时间')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), comment='角色类型')

    messages = db.relationship('UserMessage', backref='user')
    comments = db.relationship('CourseComments', backref='user')
    favorites = db.relationship('UserFavorite', backref='user_favorites')

    @property
    def password(self):
        raise AttributeError('password access denied!')

    @password.setter
    def password(self, new_password):
        self.password_hash = generate_password_hash(new_password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def has_role(self):
        role = Role.query.filter_by(name='Administrator').first()
        if role:
            return True
        else:
            return False

    def update_login_time(self):
        self.last_login = datetime.now()

    def update_logout_time(self):
        self.last_logout = datetime.now()

    def generate_confirm_token(self, expiration=3600):
        """
            生成时间json 令牌
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        result = s.dumps({'confirmed': self.id})
        return result

    def confirm(self, token):
        """
            拿到令牌进行解析
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception as e:
            return False
        if data.get('confirmed') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_forget_password_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        result = s.dumps({'forget': '@' + self.email})
        return result

    @staticmethod
    def forget_password(token):
        """
            拿到令牌进行解析
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception as e:
            return False
        result = data.get('forget')
        if result.find('@') == -1:
            return False
        return result[result.find('@') + 1:]

    def __repr__(self):
        return "<User,%s>" % self.username

    def __str__(self):
        return self.username


# class AnonymousUser(AnonymousUserMixin):
#     """
#         匿名用户
#     """
#
#     def can(self, permission):
#         return False
#
#     def is_administrator(self):
#         return False


from app import login_manager


# login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ##### 邮箱验证码  #######
class EmailVerifyCode(db.Model):
    __tablename__ = 'verify_codes'
    CODE_TYPES = (
        ('0', '注册'),
        ('1', '找回密码',),
        ('2', '修改邮箱',),
    )

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    email = db.Column(db.String(128), nullable=False, index=True, comment='发送邮箱', doc='发送邮箱')
    code = db.Column(db.String(32), nullable=False, index=True, comment='验证码', doc='验证码')
    code_type = db.Column(db.String(1), nullable=False, default='0', comment='验证码类型', doc='验证码类型')
    add_time = db.Column(db.DateTime(), default=datetime.now, comment='发送时间', doc='发送时间')

    def __repr__(self):
        return "<EmailVerifyCode,%s>" % self.code

    def __str__(self):
        return self.email


# ###### User operation  ########
class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    FAV_TYPES = (
        ('0', '课程'),
        ('1', '机构',),
        ('2', '讲师'),
    )
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    fav_id = db.Column(db.Integer, default=0, comment='收藏ID')
    fav_type = db.Column(db.Integer, default=1, comment='收藏类型')
    add_time = db.Column(db.DateTime(), default=datetime.now, comment='添加时间', doc='添加时间')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='用户ID')

    def __repr__(self):
        return "<UserFavorite,%s>" % self.fav_id


class UserAsk(db.Model):
    __tablename__ = 'user_asks'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(20), comment='咨询人名')
    mobile = db.Column(db.String(11), nullable=False, comment='联系手机号码')
    course_name = db.Column(db.String(30), comment='咨询课程名')
    add_time = db.Column(db.DateTime(), default=datetime.now, comment='添加时间', doc='添加时间')

    def __repr__(self):
        return "<UserAsk,%s>" % self.name

    def __str__(self):
        return self.name


class CourseComments(db.Model):
    __tablename__ = 'course_comments'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), comment='评论课程名')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='评论用户')
    comment = db.Column(db.String(200), comment='用户评论信息')
    add_time = db.Column(db.DateTime(), default=datetime.now, comment='添加时间', doc='添加时间')

    def __repr__(self):
        return "<CourseComments,%s,%s>" % (self.course.name, self.user.username)

    def __str__(self):
        return self.id


class UserMessage(db.Model):
    __tablename__ = 'user_messages'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    message = db.Column(db.String(256), index=True, nullable=False, comment='用户消息', doc='用户消息')
    has_read = db.Column(db.Boolean, default=0, comment='是否已读')
    add_time = db.Column(db.DateTime(), default=datetime.now, comment='添加时间', doc='添加时间')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return "<Message,%s>" % self.message

    def __str__(self):
        return self.message


# ###### 首页轮播图  ##########
class Banner(db.Model):
    __tablename__ = 'banners'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(128), nullable=True, index=True, comment='标题', doc='标题')
    url = db.Column(db.String(256), nullable=True, comment='跳转url', doc='跳转url')
    image = db.Column(db.String(256), nullable=True, comment='轮播图片', doc='轮播图片')
    index = db.Column(db.Integer, nullable=False, comment='轮播顺序', doc='轮播顺序')
    add_time = db.Column(db.DateTime, default=datetime.now, comment='添加时间', doc='添加时间')

    def __repr__(self):
        return "<Banner,%s>" % self.title

    def __str__(self):
        return self.title


# ###### 授课机构  ##########
class CityDict(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(20), comment='城市')
    desc = db.Column(db.String(200), comment='描述')
    add_time = db.Column(db.DateTime, default=datetime.now, comment='添加时间')
    courseorgs = db.relationship('CourseOrg', backref='city')

    def __repr__(self):
        return "<CityDict,%s>" % self.name

    def __str__(self):
        return self.name


class CourseOrg(db.Model):
    ORG_CATEGORY = (
        ('org', '培训机构'),
        ('colleges', '高校'),
        ('personal', '个人')
    )
    __tablename__ = 'course_orgs'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(128), index=True, unique=True, comment='授课机构')
    image = db.Column(db.String(200), nullable=True, comment='机构封面图')
    click_nums = db.Column(db.Integer, default=0, comment='点击数')
    fav_nums = db.Column(db.Integer, default=0, comment='收藏数')
    students = db.Column(db.Integer, default=0, comment='学习人数')
    category = db.Column(db.String(20), nullable=True, default='org', comment='机构类别')
    detail = db.Column(db.Text(), comment='机构介绍')
    address = db.Column(db.String(128), nullable=True, comment='地址')
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    courses = db.relationship('Course', backref='courseorg')
    teachers = db.relationship('Teacher', backref='courseorg')
    add_time = db.Column(db.DateTime, default=datetime.now, comment='添加时间', doc='添加时间')
    abstract = db.Column(db.String(128), default="权威教学", comment="机构简介")

    def __repr__(self):
        return "<CourseOrg,%s>" % self.name

    def __str__(self):
        return self.name


class Teacher(db.Model):
    __tablename__ = 'teachers'
    PROFESSIONAL = (
        ('jp', '金牌讲师'),
        ('yp', '银牌讲师'),
        ('tp', '铜牌讲师'),
    )
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(20), index=True, unique=True, comment='讲师')
    image = db.Column(db.String(100), comment='讲师头像')
    profession = db.Column(db.String(6), default='jp', comment='讲师职称')
    work_years = db.Column(db.Integer, default=0, nullable=False, comment='工作年限')
    work_company = db.Column(db.String(50), default='', comment='就职公司')
    work_position = db.Column(db.String(20), default='', comment='公司职业')
    points = db.Column(db.String(50), default='', comment='教学特点')
    fav_nums = db.Column(db.Integer, default=0, nullable=False, comment='收藏数')
    course_org_id = db.Column(db.Integer, db.ForeignKey('course_orgs.id'), comment='讲师所属机构')
    add_time = db.Column(db.DateTime, default=datetime.now, comment='添加时间', doc='添加时间')
    courses = db.relationship('Course', backref='teacher')
    birthday = db.Column(db.Date, default=date.today, comment='出生日期')
    hits = db.Column(db.Integer, default=0, nullable=False, comment='点击数')

    @property
    def click_hits(self):
        self.hits += 1
        db.session.add(self)
        db.session.commit()

    @property
    def get_profession(self):
        for elem in self.PROFESSIONAL:
            if elem[0] == self.profession:
                return elem[1]
        return '铜牌讲师'

    def __repr__(self):
        return "<Teacher,%s>" % self.name

    def __str__(self):
        return self.name


# ###### 课程  ##########
class Course(db.Model):
    __tablename__ = 'courses'
    COURSE_GRADE = (
        ('gj', '高级'),
        ('zj', '中级'),
        ('cj', '初级'),
    )
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(128), nullable=False, index=True, comment='课程名', doc='课程名')
    desc = db.Column(db.String(256), nullable=True, comment='课程描述')
    detail = db.Column(db.Text(), nullable=True, comment='课程详情')
    degree = db.Column(db.String(3), nullable=False, default='gj', comment='课程难度')
    students = db.Column(db.Integer, default=0, comment='学习人数')
    click_nums = db.Column(db.Integer, default=0, comment='点击数')
    recommend = db.Column(db.Boolean, default=False, comment='是否推荐')
    fav_nums = db.Column(db.Integer, default=0, comment='收藏人数')
    image = db.Column(db.String(100), nullable=True, comment='封面图')
    learn_time = db.Column(db.Integer, default=0, comment='学习时长(默认分钟)')
    category = db.Column(db.String(20), default='后台开发', comment='课程分类')
    tag = db.Column(db.String(20), comment='标题')
    notice = db.Column(db.String(128), comment='公告')
    youneed_know = db.Column(db.String(300), comment='课程须知')
    teacher_tell = db.Column(db.String(300), comment='老师告诉你')
    courseorg_id = db.Column(db.Integer, db.ForeignKey('course_orgs.id'), comment='课程所属机构')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), comment='课程讲师')
    add_time = db.Column(db.DateTime, default=datetime.now, comment='添加时间', doc='添加时间')
    lessons = db.relationship('Lesson', backref='course')
    is_banner = db.Column(db.Boolean, default=False, nullable=False, comment='是否轮播')

    @property
    def get_degree(self):
        tmp = []
        for elem in self.COURSE_GRADE:
            if self.degree in elem:
                tmp = elem
                break
        return tmp[1]

    def __repr__(self):
        return "<Course,%s>" % self.name

    def __str__(self):
        return self.name


class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(50), comment='章节')
    learn_times = db.Column(db.Integer, comment='学习时长(分钟)')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), comment='所属课程')
    add_time = db.Column(db.DateTime, default=datetime.now, comment='添加时间', doc='添加时间')
    videos = db.relationship('Video', backref='lesson')

    def __repr__(self):
        return "<Lession,%s>" % self.names

    def __str__(self):
        return self.name


class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(50), comment='视频名')
    path = db.Column(db.String(200), comment='文件路径')
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), comment='所属章节')
    learn_times = db.Column(db.Integer, default=0, comment='学习时长')
    add_time = db.Column(db.DateTime, default=datetime.now, comment='添加时间', doc='添加时间')

    def __repr__(self):
        return "<Video,%s>" % self.name

    def __str__(self):
        return self.name


class CourseResource(db.Model):
    __tablename__ = 'course_resources'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    course = db.Column(db.Integer, db.ForeignKey('courses.id'), comment='资源所属课程')
    name = db.Column(db.String(100), comment='资源名称')
    download = db.Column(db.String(100), comment='下载资源地址')
    add_time = db.Column(db.DateTime, default=datetime.now, comment='添加时间', doc='添加时间')

    def __repr__(self):
        return "<CourseResource,%s>" % self.name

    def __str__(self):
        return self.name


# Create models
class File(db.Model):
    """
        用户富文本存储文件
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    path = db.Column(db.String(128))

    def __str__(self):
        return self.name


class Image(db.Model):
    """
        用户富文本存储图片
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    path = db.Column(db.String(128))

    def __str__(self):
        return self.name
