# -*- coding:utf-8 -*-
import hashlib
from flask import current_app, render_template, request, redirect, url_for,Blueprint
import flask_login
from ..models.dbORM import User as U
from app import db,login_manager
web = Blueprint('web',__name__)

@web.route('/')
def protected():
    return "hello world"