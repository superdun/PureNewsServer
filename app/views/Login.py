# -*- coding:utf-8 -*-
import hashlib
from flask import current_app, render_template, request, redirect, url_for,Blueprint
import flask_login
from ..models.dbORM import User as U
from app import db,login_manager
login_bp = Blueprint('login',__name__)


def getusers():
    users = {}
    raw_users = U.query.all()

    for user in raw_users:
        users[user.name] = {'password': user.password, 'username': user.name,
                            'id': user.id}
    return users

class User(flask_login.UserMixin):
    pass
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    users = getusers()

    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect('admin')
        return render_template('login.html')

    username = request.form['username']
    if username not in users:
        return 'wrong username'
    md5 = hashlib.md5()
    if request.form['password'] == "":
        return render_template('login.html')
    md5.update(request.form['password'])
    psswd = md5.hexdigest()
    if psswd == users[username]['password']:
        user = User()
        user.id = username
        flask_login.login_user(user)
        return redirect(url_for('login.protected'))

    return render_template('login.html')


@login_bp.route('/protected')
@flask_login.login_required
def protected():
    return redirect('/')


@login_bp.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect('/')
