import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY") or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASK_MAIL_SUBJECT_PREFIX = "[Flasky]"
    FLASK_MAIL_SENDER = os.getenv("MAIL_USERNAME")
    FLASK_ADMIN = os.getenv("FLASK_ADMIN")
    FLASK_PER_PAGE = 8  # 分页，当页显示最大数据条目
    BABEL_DEFAULT_LOCALE = 'zh_CN'
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=10)
    CKEDITOR_FILE_UPLOADER = 'upload'  # 设置ckeditor 富文本上传 参数

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUT = True
    MAIL_SERVER = "smtp.163.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_MAX_EMAILS = 40
    MAIL_DEBUG = True
    MAIL_DEFAULT_HTML = "%(username)s 欢迎加入Flask大家庭!"
    SQLALCHEMY_DATABASE_URI = os.getenv("MXONLINE_DATABASE_URL") or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL") or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

if __name__ == "__main__":
    print(os.getenv("FLASK_CONFIG"))
    print(os.getenv("MXONLINE_DATABASE_URL"))
    print(config["development"])
    print(Config.FLASK_MAIL_SENDER)
    print(os.getenv("MAIL_PASSWORD"))
    print(Config.FLASK_ADMIN)
    print(basedir)
