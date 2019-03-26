# -*- coding:utf-8 -*-
import os, sys
from  flask import Blueprint, request, current_app, url_for, jsonify,abort
from ..models.dbORM import *
from ..modules.Wechat import *
from datetime import datetime,timedelta
from ..helpers.session3rd import *
from ..modules.Cache import *
from app import db
import  json
import requests
import time
api = Blueprint('api', __name__)

def getWechatAuth():
    appid = current_app.config.get("WECHAT_APP_ID")
    appsecret = current_app.config.get("WECHAT_APP_SECERET")
    return WechatAuth(appid,appsecret)
#
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
    return jsonify({"status": "ok","userInfo":{"nickName":userInfo["nickName"], "avatarUrl":userInfo["avatarUrl"]}})

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
    feedback = Feedback(detail=fb,created_at=datetime.now(),openid=openid)
    db.session.add(feedback)
    db.session.commit()
    return jsonify({"status": "ok"})


@api.route("/status",methods=['POST'])
def WeStatus():
    session3rd =request.json["session3rd"]
    cr = WeCheckLogin(session3rd)
    if not cr:
        abort(404)
    cache = getCache()
    openid = cache.get(session3rd)[0]
    status = request.json["status"]
    loc = request.json["loc"]
    lat = request.json["lat"]
    lon = request.json["lon"]
    customer = Customer.query.filter_by(openid=openid).first()
    flus = customer.flus.order_by(db.desc(Flu.id))
    if flus.count()==0:
        if status==0:
            return abort(404)
    elif flus[0].status == status :
        return abort(404)


    if status==0:
        currentFlu = flus[0]
        currentFlu.status=0
        currentFlu.end_at=datetime.now()
        currentFlu.daydelta = (datetime.now()-currentFlu.start_at).days+1
        # if currentFlu.daydelta<1:
        #     return {"status": "error","msg":"哪有这么快感冒就好的！"}
        if customer.count:
            customer.count = customer.count+currentFlu.daydelta
        else:
            customer.count = currentFlu.daydelta
        customer.status = 0
        db.session.add(currentFlu)
        db.session.add(customer)
        db.session.commit()
    else:
       flu = Flu(start_at = datetime.now(),status=1,openid=openid,daydelta=0,
                 loc=loc,lat=lat,lon=lon)
       customer.loc = loc
       customer.status = 1
       customer.lat = lat
       customer.lon = lon
       db.session.add(customer)
       db.session.add(flu)
       db.session.commit()
    return jsonify({"status": "ok",'stat':status})

@api.route("/info")
def WeInfo():

    loc = request.args.get("loc")
    session3rd =request.args.get("session3rd")
    cr = WeCheckLogin(session3rd)
    if not cr:
        return jsonify({"status": "failed"})
    cache = getCache()
    openid = cache.get(session3rd)[0]
    customer = Customer.query.filter_by(openid=openid).first()
    if not customer:
        return abort(404)
    flus = [{
        "start_at_raw": flu.start_at,
        "end_at_raw": flu.end_at,
        "start_at":flu.start_at.strftime("%Y-%m-%d") if flu.start_at else "NAN",
        "end_at": flu.end_at.strftime("%Y-%m-%d") if flu.end_at else u"现在",
        "status": flu.status,
        "daydelta": (datetime.now() -flu.start_at).days+1  if flu.status else (flu.end_at -flu.start_at).days+1,
        "loc": flu.loc,
    } for flu in customer.flus.order_by(db.desc(Flu.id))]
    total_count = len(flus)
    if total_count:
        currentFlu = flus[0]
        if currentFlu["status"] == 1:
            status = 1
            dayCount = (datetime.now() - currentFlu["start_at_raw"]).days+1
        else:
            status = 0
            dayCount = 0
    else:
        status = 0
        dayCount = 0
    totalIllPeople = Customer.query.filter_by(status=1)
    total_peopleCount = totalIllPeople.count()
    if loc:
        peopleNearbyCount = totalIllPeople.filter_by(loc=loc).count()
    else:
        peopleNearbyCount = 0

    if customer.count:
        total_dayCount = customer.count+dayCount
    else:
        total_dayCount = dayCount
    if total_count:
        averageCount = total_dayCount/total_count
    else:
        averageCount = 0
    list = flus
    greaterCount = Customer.query.filter(Customer.count>=total_count).count()
    allCount  = Customer.query.count()
    defeat = int(greaterCount/allCount)*100
    markers = [{"latitude":p.lat,"longitude":p.lon,"iconPath":p.img,"id":p.id,"name":"","width":30,"height":30}  for p in totalIllPeople.all()]
    info = {
        'total_peopleCount': total_peopleCount,
        'peopleNearbyCount': peopleNearbyCount,
        'dayCount': dayCount,
        'markers': markers,
        'status': status,
        'total_count': total_count,
        'total_dayCount': total_dayCount,
        'averageCount': averageCount,
        'defeat': defeat,
        'list': list
    }
    return jsonify(info)


@api.route("/weather")
def WeWeather():
    # weatherkey = current_app.config.get("WEATHER_KEY")
    # FUTURE_WEATHER_URL = current_app.config.get("FUTURE_WEATHER_URL")
    # NOW_WEATHER_URL = current_app.config.get("NOW_WEATHER_URL")
    # HISTORY_WEATHER_URL = current_app.config.get("HISTORY_WEATHER_URL")
    # NOW_AIR_URL = current_app.config.get("NOW_AIR_URL")
    # city = request.args.get("city")
    # para1={"location":city,"key":weatherkey}
    #
    # FUTURE_WEATHER = requests.get(url=FUTURE_WEATHER_URL,params=para1).json()
    # if FUTURE_WEATHER["HeWeather6"][0]["status"]!="ok":
    #     abort(404)
    # else:
    #     cid =FUTURE_WEATHER["HeWeather6"][0]["basic"]["cid"]
    # para2 = {"location": cid, "key": weatherkey, "date": str(datetime.today().date() - timedelta(days=1))}
    # NOW_WEATHER = requests.get(url=NOW_WEATHER_URL, params=para1).json()
    # HISTORY_WEATHER = requests.get(url=HISTORY_WEATHER_URL, params=para2).json()
    # NOW_AIR = requests.get(url=NOW_AIR_URL, params=para1).json()
    # for i in [FUTURE_WEATHER,NOW_WEATHER,HISTORY_WEATHER,NOW_AIR]:
    #     if i["HeWeather6"][0]["status"]!="ok":
    #         abort(404)
    # return jsonify({"yesterday":HISTORY_WEATHER["HeWeather6"][0],"now":NOW_WEATHER["HeWeather6"][0],"future":FUTURE_WEATHER["HeWeather6"][0],"air":NOW_AIR["HeWeather6"][0],"city":city})
    return jsonify({'city': u'\u6768\u6d66\u533a', 'future': {u'status': u'ok', u'daily_forecast': [{u'uv_index': u'0', u'wind_sc': u'3-4', u'tmp_min': u'9', u'cond_txt_d': u'\u9634', u'vis': u'25', u'wind_spd': u'21', u'hum': u'78', u'cond_txt_n': u'\u591a\u4e91', u'pop': u'5', u'wind_deg': u'121', u'pcpn': u'0.0', u'wind_dir': u'\u4e1c\u5357\u98ce', u'cond_code_d': u'104', u'date': u'2019-03-18', u'tmp_max': u'12', u'cond_code_n': u'101', u'pres': u'1018'}, {u'uv_index': u'0', u'wind_sc': u'4-5', u'tmp_min': u'11', u'cond_txt_d': u'\u591a\u4e91', u'vis': u'24', u'wind_spd': u'28', u'hum': u'80', u'cond_txt_n': u'\u5c0f\u96e8', u'pop': u'0', u'wind_deg': u'150', u'pcpn': u'0.0', u'wind_dir': u'\u4e1c\u5357\u98ce', u'cond_code_d': u'101', u'date': u'2019-03-19', u'tmp_max': u'19', u'cond_code_n': u'305', u'pres': u'1008'}, {u'uv_index': u'0', u'wind_sc': u'3-4', u'tmp_min': u'13', u'cond_txt_d': u'\u5c0f\u96e8', u'vis': u'24', u'wind_spd': u'21', u'hum': u'74', u'cond_txt_n': u'\u5c0f\u96e8', u'pop': u'55', u'wind_deg': u'310', u'pcpn': u'1.0', u'wind_dir': u'\u897f\u5317\u98ce', u'cond_code_d': u'305', u'date': u'2019-03-20', u'tmp_max': u'23', u'cond_code_n': u'305', u'pres': u'1011'}], u'update': {u'loc': u'2019-03-18 21:55', u'utc': u'2019-03-18 13:55'}, u'basic': {u'tz': u'+8.00', u'cid': u'CN101021700', u'lon': u'121.52279663', u'admin_area': u'\u4e0a\u6d77', u'parent_city': u'\u4e0a\u6d77', u'lat': u'31.27075577', u'cnty': u'\u4e2d\u56fd', u'location': u'\u6768\u6d66'}}, 'now': {u'status': u'ok', u'now': {u'tmp': u'11', u'wind_sc': u'0', u'cond_txt': u'\u591a\u4e91', u'vis': u'9', u'hum': u'78', u'cond_code': u'101', u'wind_deg': u'2', u'pcpn': u'0.0', u'pres': u'1017', u'wind_spd': u'1', u'wind_dir': u'\u5317\u98ce', u'fl': u'11', u'cloud': u'10'}, u'update': {u'loc': u'2019-03-18 21:55', u'utc': u'2019-03-18 13:55'}, u'basic': {u'tz': u'+8.00', u'cid': u'CN101021700', u'lon': u'121.52279663', u'admin_area': u'\u4e0a\u6d77', u'parent_city': u'\u4e0a\u6d77', u'lat': u'31.27075577', u'cnty': u'\u4e2d\u56fd', u'location': u'\u6768\u6d66'}}, 'yesterday': {u'status': u'ok', u'daily_weather': {u'sr': u'06:00', u'tmp_min': u'9', u'ss': u'18:03', u'hum': u'90', u'pcpn': u'0', u'ms': u'03:04', u'mr': u'13:46', u'date': u'2019-03-17', u'tmp_max': u'22', u'pres': u'975'}, u'hourly_weather': [{u'tmp': u'12', u'wind_sc': u'0', u'cond_txt': u'\u591a\u4e91', u'hum': u'69', u'cond_code': u'101', u'wind_dir': u'\u4e1c\u98ce', u'time': u'2019-03-17 00:00', u'wind_spd': u'1', u'pres': u'1022'}, {u'tmp': u'12', u'wind_sc': u'0', u'cond_txt': u'\u591a\u4e91', u'hum': u'74', u'cond_code': u'101', u'wind_dir': u'\u5357\u98ce', u'time': u'2019-03-17 01:00', u'wind_spd': u'1', u'pres': u'1022'}, {u'tmp': u'11', u'wind_sc': u'0', u'cond_txt': u'\u591a\u4e91', u'hum': u'79', u'cond_code': u'101', u'wind_dir': u'\u5357\u98ce', u'time': u'2019-03-17 02:00', u'wind_spd': u'1', u'pres': u'1022'}, {u'tmp': u'10', u'wind_sc': u'0', u'cond_txt': u'\u591a\u4e91', u'hum': u'81', u'cond_code': u'101', u'wind_dir': u'\u5317\u98ce', u'time': u'2019-03-17 03:00', u'wind_spd': u'1', u'pres': u'1021'}, {u'tmp': u'10', u'wind_sc': u'0', u'cond_txt': u'\u591a\u4e91', u'hum': u'84', u'cond_code': u'101', u'wind_dir': u'\u5317\u98ce', u'time': u'2019-03-17 04:00', u'wind_spd': u'1', u'pres': u'1021'}, {u'tmp': u'10', u'wind_sc': u'0', u'cond_txt': u'\u591a\u4e91', u'hum': u'87', u'cond_code': u'101', u'wind_dir': u'\u5317\u98ce', u'time': u'2019-03-17 05:00', u'wind_spd': u'1', u'pres': u'1021'}, {u'tmp': u'9', u'wind_sc': u'0', u'cond_txt': u'\u6674', u'hum': u'89', u'cond_code': u'100', u'wind_dir': u'\u5317\u98ce', u'time': u'2019-03-17 06:00', u'wind_spd': u'1', u'pres': u'1021'}, {u'tmp': u'10', u'wind_sc': u'0', u'cond_txt': u'\u6674', u'hum': u'90', u'cond_code': u'100', u'wind_dir': u'\u5317\u98ce', u'time': u'2019-03-17 07:00', u'wind_spd': u'1', u'pres': u'1022'}, {u'tmp': u'11', u'wind_sc': u'0', u'cond_txt': u'\u6674', u'hum': u'81', u'cond_code': u'100', u'wind_dir': u'\u4e1c\u98ce', u'time': u'2019-03-17 08:00', u'wind_spd': u'1', u'pres': u'1023'}, {u'tmp': u'17', u'wind_sc': u'0', u'cond_txt': u'\u6674', u'hum': u'53', u'cond_code': u'100', u'wind_dir': u'\u5357\u98ce', u'time': u'2019-03-17 09:00', u'wind_spd': u'1', u'pres': u'1023'}, {u'tmp': u'19', u'wind_sc': u'1', u'cond_txt': u'\u6674', u'hum': u'33', u'cond_code': u'100', u'wind_dir': u'\u897f\u98ce', u'time': u'2019-03-17 10:00', u'wind_spd': u'4', u'pres': u'1024'}, {u'tmp': u'21', u'wind_sc': u'1', u'cond_txt': u'\u591a\u4e91', u'hum': u'27', u'cond_code': u'101', u'wind_dir': u'\u897f\u5357\u98ce', u'time': u'2019-03-17 11:00', u'wind_spd': u'3', u'pres': u'1024'}, {u'tmp': u'22', u'wind_sc': u'1', u'cond_txt': u'\u591a\u4e91', u'hum': u'21', u'cond_code': u'101', u'wind_dir': u'\u897f\u98ce', u'time': u'2019-03-17 12:00', u'wind_spd': u'3', u'pres': u'1023'}, {u'tmp': u'22', u'wind_sc': u'1', u'cond_txt': u'\u591a\u4e91', u'hum': u'18', u'cond_code': u'101', u'wind_dir': u'\u897f\u5317\u98ce', u'time': u'2019-03-17 13:00', u'wind_spd': u'4', u'pres': u'1023'}, {u'tmp': u'22', u'wind_sc': u'2', u'cond_txt': u'\u591a\u4e91', u'hum': u'24', u'cond_code': u'101', u'wind_dir': u'\u4e1c\u5317\u98ce', u'time': u'2019-03-17 14:00', u'wind_spd': u'11', u'pres': u'1022'}, {u'tmp': u'21', u'wind_sc': u'1', u'cond_txt': u'\u591a\u4e91', u'hum': u'31', u'cond_code': u'101', u'wind_dir': u'\u4e1c\u5317\u98ce', u'time': u'2019-03-17 15:00', u'wind_spd': u'3', u'pres': u'1021'}, {u'tmp': u'19', u'wind_sc': u'1', u'cond_txt': u'\u591a\u4e91', u'hum': u'30', u'cond_code': u'101', u'wind_dir': u'\u4e1c\u98ce', u'time': u'2019-03-17 16:00', u'wind_spd': u'3', u'pres': u'1020'}, {u'tmp': u'17', u'wind_sc': u'1', u'cond_txt': u'\u591a\u4e91', u'hum': u'38', u'cond_code': u'101', u'wind_dir': u'\u4e1c\u5317\u98ce', u'time': u'2019-03-17 17:00', u'wind_spd': u'5', u'pres': u'1020'}, {u'tmp': u'15', u'wind_sc': u'0', u'cond_txt': u'\u591a\u4e91', u'hum': u'61', u'cond_code': u'101', u'wind_dir': u'\u4e1c\u5317\u98ce', u'time': u'2019-03-17 18:00', u'wind_spd': u'1', u'pres': u'1021'}, {u'tmp': u'13', u'wind_sc': u'1', u'cond_txt': u'\u591a\u4e91', u'hum': u'75', u'cond_code': u'101', u'wind_dir': u'\u4e1c\u5317\u98ce', u'time': u'2019-03-17 19:00', u'wind_spd': u'2', u'pres': u'1022'}, {u'tmp': u'12', u'wind_sc': u'1', u'cond_txt': u'\u9634', u'hum': u'79', u'cond_code': u'104', u'wind_dir': u'\u4e1c\u5317\u98ce', u'time': u'2019-03-17 20:00', u'wind_spd': u'2', u'pres': u'1022'}, {u'tmp': u'12', u'wind_sc': u'0', u'cond_txt': u'\u9634', u'hum': u'85', u'cond_code': u'104', u'wind_dir': u'\u897f\u5357\u98ce', u'time': u'2019-03-17 21:00', u'wind_spd': u'1', u'pres': u'1022'}, {u'tmp': u'12', u'wind_sc': u'1', u'cond_txt': u'\u9634', u'hum': u'87', u'cond_code': u'104', u'wind_dir': u'\u4e1c\u5317\u98ce', u'time': u'2019-03-17 22:00', u'wind_spd': u'3', u'pres': u'1022'}, {u'tmp': u'12', u'wind_sc': u'0', u'cond_txt': u'\u9634', u'hum': u'89', u'cond_code': u'104', u'wind_dir': u'\u5317\u98ce', u'time': u'2019-03-17 23:00', u'wind_spd': u'1', u'pres': u'1022'}], u'basic': {u'tz': u'+8.0', u'cid': u'CN101021700', u'lon': u'121.52279663', u'admin_area': u'\u4e0a\u6d77', u'parent_city': u'\u4e0a\u6d77', u'lat': u'31.27075577', u'cnty': u'\u4e2d\u56fd', u'location': u'\u6768\u6d66'}}, 'air': {u'status': u'ok', u'air_now_city': {u'pub_time': u'2019-03-18 22:00', u'co': u'0.7', u'qlty': u'\u826f', u'pm10': u'42', u'o3': u'23', u'so2': u'3', u'pm25': u'44', u'main': u'PM2.5', u'aqi': u'62', u'no2': u'103'}, u'update': {u'loc': u'2019-03-18 21:55', u'utc': u'2019-03-18 13:55'}, u'basic': {u'tz': u'+8.00', u'cid': u'CN101021700', u'lon': u'121.52279663', u'admin_area': u'\u4e0a\u6d77', u'parent_city': u'\u4e0a\u6d77', u'lat': u'31.27075577', u'cnty': u'\u4e2d\u56fd', u'location': u'\u6768\u6d66'}}})




