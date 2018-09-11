from flask import render_template, redirect, url_for
from flask_login import current_user

from . import index


@index.route('/')
def index():
    return render_template('index/index.html')
