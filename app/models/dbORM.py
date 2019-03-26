# -*- coding:utf-8 -*-
from datetime import datetime
from app import db
from datetime import date
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
