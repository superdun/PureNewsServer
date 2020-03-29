# -*- coding:utf-8 -*-
from datetime import datetime
from app import db
from datetime import date
class Color(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color= db.Column(db.String(1000))
    jname1= db.Column(db.String(1000))
    jname2= db.Column(db.String(1000))
    cname= db.Column(db.String(1000))
    jprop1 = db.Column(db.String(1000))
    jprop2= db.Column(db.String(1000))
    cprop1= db.Column(db.String(1000))
    cprop2= db.Column(db.String(1000))
    fontcolor = db.Column(db.String(1000))
    spaceimg = db.Column(db.String(1000))
    def __repr__(self):
        return self.id

class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img= db.Column(db.String(1000))
    name= db.Column(db.String(1000))
    description= db.Column(db.Text())
    srcimg= db.Column(db.String(1000))
    srcurl = db.Column(db.String(1000))
    def __repr__(self):
        return self.id

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    openid = db.Column(db.String(120))
    img = db.Column(db.String(200))
    unionid = db.Column(db.String(120))
    name = db.Column(db.String(120))
    feedbacks = db.relationship('Feedback', backref='Customer', lazy='dynamic')
    flus = db.relationship('Flu', backref='Customer', lazy='dynamic')
    count = db.Column(db.Integer)
    loc = db.Column(db.String(120))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    status = db.Column(db.Integer)
    def __repr__(self):
        return self.id

class Flu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    status = db.Column(db.Integer)

    openid = db.Column(db.String(80), db.ForeignKey('customer.openid'))
    daydelta =  db.Column(db.Integer)
    loc = db.Column(db.String(120))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    def __repr__(self):
        return self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    password = db.Column(db.String(80))


    def __repr__(self):
        return self.id

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    detail = db.Column(db.String(8000))
    created_at = db.Column(db.DateTime, default=datetime.now())
    openid = db.Column(db.String(80), db.ForeignKey('customer.openid'))

    def __repr__(self):
        return self.id
