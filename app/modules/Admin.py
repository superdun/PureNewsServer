# -*- coding: utf-8 -*-
from flask import request
import os
import os.path as op
import time
from flask_admin import Admin
import flask_login
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.view import func
from jinja2 import Markup
from flask import current_app
from ..models.dbORM import *
from ..helpers import thumb
from flask_qiniustorage import Qiniu
from wtforms import SelectField, PasswordField
from flask_admin import BaseView, expose
import hashlib
from app import db


def getQiniuDomain():
    return current_app.config.get('QINIU_BUCKET_DOMAIN', '')


def getUploadUrl():
    return current_app.config.get('UPLOAD_URL')


def date_format(value):
    return time.strftime(u'%Y/%m/%d %H:%M:%S', time.localtime(float(value)))


def img_url_format(value):
    return Markup("<img src='%s'>" % ("http://" + getQiniuDomain() + value))


def dashboard():
    admin = Admin(current_app, name=u'PureNews后台管理')
    admin.add_view(UserView(User, db.session, name=u"管理员管理"))
    admin.add_view(TagView(Tag, db.session, name=u"标签"))
    admin.add_view(CustomerView(Customer, db.session, name=u"用户"))
    admin.add_view(PostView(Post, db.session, name=u"文章"))
    admin.add_view(AttitudeView(Attitude, db.session, name=u"点赞"))

class UploadWidget(form.ImageUploadInput):
    def get_url(self, field):
        if field.thumbnail_size:
            filename = field.thumbnail_fn(field.data)
        else:
            filename = field.data

        if field.url_relative_path:
            filename = "http://" + field.url_relative_path + filename
        return filename


class ImageUpload(form.ImageUploadField):
    widget = UploadWidget()

    def _save_file(self, data, filename):
        path = self._get_path(filename)
        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path), self.permission | 0o111)

        data.seek(0)
        data.save(path)
        qiniu_store = Qiniu(current_app)
        with open(path, 'rb') as fp:
            ret, info = qiniu_store.save(fp, filename)
            if 200 != info.status_code:
                raise Exception("upload to qiniu failed", ret)
            # shutil.rmtree(os.path.dirname(path))
            return filename


class AdminModel(ModelView):
    column_default_sort = ('id', True)

    def is_accessible(self):
        if flask_login.current_user.is_authenticated:
            return True
        else:
            return False


# super admin models



class UserView(AdminModel):

    def on_model_change(self, form, model, is_created):
        password = model.password
        md5 = hashlib.md5()
        md5.update(password)
        model.password = md5.hexdigest()


class TagView(AdminModel):
    pass


class CustomerView(AdminModel):
    form_extra_fields={
        'img': ImageUpload(u'头像', base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                           url_relative_path=getQiniuDomain()),

    }

class AttitudeView(AdminModel):
    pass



class PostView(AdminModel):

    @property
    def form_extra_fields(self):
        return {
            'img': ImageUpload(u'图片', base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                               url_relative_path=getQiniuDomain()),
            'status': SelectField(u'状态', choices=(("delete", u"已删除"), ("publish", u"发布")))
        }
