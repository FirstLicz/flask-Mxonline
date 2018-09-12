from flask_mail import Message
from threading import Thread
from flask import current_app, render_template

from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """
    :param to:          email
    :param subject:     str
    :param template:    dict
    :param kwargs:
    :return:
    """
    app = current_app._get_current_object()
    msg = Message(subject=app.config['FLASK_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASK_MAIL_SENDER'], recipients=[to])
    msg.html = "<p>%(username)s欢迎加入Flask大家庭！以下是激活链接:%(url)s</p>" % template
    thr = Thread(target=send_async_email, args=(app, msg))
    thr.start()
    return thr