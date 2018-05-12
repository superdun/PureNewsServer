# -*- coding:utf-8 -*-
from datetime import datetime
from app import db
from datetime import date


class Attitude(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer, db.ForeignKey('post.id'))
    openid = db.Column(db.Integer, db.ForeignKey('customer.openid'))
    status = db.Column(db.Integer)
    def __repr__(self):
        return self.id
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    title = db.Column(db.String(80))
    img = db.Column(db.String(200))
    detail = db.Column(db.String(5000))
    agreecount = db.Column(db.Integer,default=0)
    disagreecount = db.Column(db.Integer,default=0)
    comment = db.Column(db.String(5000))
    tagid = db.Column(db.Integer, db.ForeignKey('tag.id'))
    customers = db.relationship('Customer', secondary="attitude", backref='Post', lazy='dynamic')
    day = db.Column(db.Date,default=date.today())
    status = db.Column(db.String(200),default="publish")
    def __repr__(self):
        return self.title

    @classmethod
    def query(cls):
        original_query = db.session.query(cls)
        return original_query.filter_by(day=date.today(),status="publish")

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    posts = db.relationship('Post', backref='Tag', lazy='dynamic')
    def __repr__(self):
        return self.name






class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    openid = db.Column(db.String(120))
    img = db.Column(db.String(200))
    posts = db.relationship('Post', secondary="attitude",backref='Customer', lazy='dynamic')
    unionid = db.Column(db.String(120))
    name = db.Column(db.String(120))
    def __repr__(self):
        return self.name



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    password = db.Column(db.String(80))


    def __repr__(self):
        return self.name

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    detail = db.Column(db.String(8000))
    created_at = db.Column(db.DateTime, default=datetime.now())
    openid = db.Column(db.String(80), db.ForeignKey('customer.openid'))

    def __repr__(self):
        return self.id
