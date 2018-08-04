# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import random
import requests
import youtube_dl
import requests
from  flask import Blueprint, request, render_template, current_app, jsonify
from ..models.dbORM import Kuma_kuma
from datetime import datetime
import os
from app import db

kuma = Blueprint('kuma', __name__)


def string_toDatetime(string):
    ts = string.split(".")[0]
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")


@kuma.route('/')
def KumaWeb():
    kumas = Kuma_kuma.query.order_by(Kuma_kuma.created_at.desc()).all()

    return render_template("kuma/index.html",kumas=kumas)
filename=""
imgname=""
@kuma.route('/<id>')
def KumaVideoWeb(id):
    kuma = Kuma_kuma.query.filter_by(id=id).first()
    return render_template("kuma/video.html",kuma=kuma)
filename=""
imgname=""
def my_hook(d):
    global filename,imgname
    if d['status'] == 'finished':

        filepath = d['filename']
        imgpath = os.path.splitext(d['filename'])[0]+'.jpg'
        filename = os.path.basename(filepath)
        imgname = os.path.basename(imgpath)
    return [filename,imgname]
@kuma.route('/fetch')
def KumaFetchApi():
    my_proxies = current_app.config.get("PROXY")
    r = requests.get(
        "https://content.googleapis.com/youtube/v3/playlistItems?playlistId=PL2nNLUYH9TlTTR3BHGO62PaJ8lkP9QnjJ&maxResults=50&part=snippet%2CcontentDetails&key=AIzaSyA1l98H4DYII8Y8P5yWHX6KimsrVoO7q3Q",
        proxies=my_proxies)
    items = r.json()["items"]
    count = 0
    try:
        for i in items:

            title = i["snippet"]["title"]
            created_at = string_toDatetime(i["snippet"]["publishedAt"])
            url = "https://www.youtube.com/watch?v=%s" % i["snippet"]["resourceId"]["videoId"]
            hasKuma = Kuma_kuma.query.filter_by(title=title).first()
            if not hasKuma:
                ydl_opts = {"progress_hooks":[my_hook],"writethumbnail":current_app.config.get("FILE_FOLDER") + i["snippet"]["resourceId"]["videoId"]+".jpg"
                ,'format': 'best', "proxy": "http://127.0.0.1:1080",
                            "outtmpl": current_app.config.get("FILE_FOLDER") + "%(id)s.%(ext)s"}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                if filename=="" or imgname=="":
                    return jsonify({"status": "failed","count":count})
                kuma = Kuma_kuma(img=imgname, title=title, status="ok", url=filename, created_at=created_at)
                db.session.add(kuma)
                db.session.commit()
                count = count + 1
        return jsonify({"status": "ok", "count": count})

    except:
        return jsonify({"status": "failed"})
    print r.json()["items"][0]
