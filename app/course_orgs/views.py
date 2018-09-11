from flask import render_template, redirect, url_for, make_response, session, request, Response
from flask_login import login_user, logout_user, current_user, login_required
from io import BytesIO

from . import org


@org.route('/list/')
def org_list():
    return render_template('org/org-list.html')
