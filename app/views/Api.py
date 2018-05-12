# -*- coding:utf-8 -*-
import os, sys
from  flask import Blueprint, request, current_app, url_for, jsonify
from ..models.dbORM import *
from ..modules.Wechat import *
from datetime import datetime
from ..helpers.session3rd import *
from ..modules.Cache import *
from app import db
import  json
api = Blueprint('api', __name__)

def getWechatAuth():
    appid = current_app.config.get("WECHAT_APP_ID")
    appsecret = current_app.config.get("WECHAT_APP_SECERET")
    return WechatAuth(appid,appsecret)

@api.route("/auth")
def WeAuth():
    code =request.args.get("code")
    wa = getWechatAuth()
    wa.fetch_session_key(code)
    session = gen_3rdsession(wa.open_id)
    cache = getCache()
    cache.set(session,[wa.open_id,wa.session_key],60*60*24*29)
    customer = Customer.query.filter_by(openid = wa.open_id).first()
    if not customer:
        customer = Customer(openid = wa.open_id,created_at = datetime.now(),unionid = wa.union_id)
        db.session.add(customer)
        db.session.commit()
    return session

def WeCheckLogin(session3rd):
    cache = getCache()
    session3rd =request.args.get("session3rd")
    if cache.get(session3rd):
        openid = cache.get(session3rd)[0]
        customer = Customer.query.filter_by(openid=openid).first()
        if  not customer:

            return False
        else:
            return True
    else:
        return False
@api.route("/getuserinfo")
def WeGetUserInfo():
    session3rd =request.args.get("session3rd")
    cr = WeCheckLogin(session3rd)
    if not cr:
        return jsonify({"status": "failed"})

    userInfo = json.loads(request.args.get("userInfo"))
    cache = getCache()
    openid = cache.get(session3rd)[0]
    customer = Customer.query.filter_by(openid=openid).first()
    if not  customer.img:
        customer.img = userInfo["avatarUrl"]
        customer.name = userInfo["nickName"]
        db.session.add(customer)
        db.session.commit()
    return jsonify({"status": "ok"})

@api.route("/feedback")
def WeFeedback():
    fb = request.args.get("feedback")
    session3rd =request.args.get("session3rd")
    cr = WeCheckLogin(session3rd)
    if not cr:
        return jsonify({"status": "failed"})


    cache = getCache()
    openid = cache.get(session3rd)[0]
    currentFB = Feedback.query.filter_by(openid=openid).order_by(Feedback.id.desc()).first()
    FBTimeRange = current_app.config.get("FBTIME_RANGE")
    if currentFB:
        nowdate = datetime.now()
        if (nowdate-currentFB.created_at).seconds<FBTimeRange:
            return jsonify({"status": "denied"})
    feedback = Feedback(detail=fb,created_at=datetime.now(),openid=openid )
    db.session.add(feedback)
    db.session.commit()
    return jsonify({"status": "ok"})

@api.route("/attitude")
def WeAttitude():
    at = int(request.args.get("attitude"))
    postid = request.args.get("postid")
    session3rd =request.args.get("session3rd")
    cr = WeCheckLogin(session3rd)
    if not cr:
        return jsonify({"status": "failed"})
    if not postid:
        return jsonify({"status": "failed"})
    try:
        postid = int(postid)
    except:
        return jsonify({"status": "failed"})
    cache = getCache()
    openid = cache.get(session3rd)[0]
    attitude = Attitude.query.filter_by(openid=openid, postid=postid).first()
    if attitude:
        return jsonify({"status": "denied"})
    else:

        attitude = Attitude(openid=openid,postid=postid,status=at)
        post = Post.query.filter_by(id = postid).first()
        if at==1:
            post.agreecount = post.agreecount+1
        elif at==-1:
            post.disagreecount = post.disagreecount+1
        db.session.add(post)
        db.session.add(attitude)
        db.session.commit()
        return jsonify({"status": "ok"})



