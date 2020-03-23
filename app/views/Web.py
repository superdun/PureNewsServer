# -*- coding:utf-8 -*-
import hashlib
from flask import current_app, render_template, request, redirect, url_for, Blueprint, abort
import flask_login
from ..models.dbORM import Color
from app import db, login_manager
web = Blueprint('web', __name__)


@web.route('/')
def protected():
    return "hello world"


@web.route('/birthcolor')
def birthcolorList():
    colors = Color.query.all()
    return render_template("game/colorList.html", colors=colors)


@web.route('/birthcolor/<id>')
def birthcolor(id):
    color = Color.query.filter_by(id=id).first()
    if color:
        return render_template("game/color.html", color=color)
    else:
        abort(404)


@web.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404



