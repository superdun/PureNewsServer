# -*- coding:utf-8 -*-
import random

from  flask import Blueprint, request, render_template, make_response

game = Blueprint('game', __name__)


@game.route('/thanos')
def Thanos():
    if 'status' in request.cookies:
        status = int(request.cookies.get('status'))
    else:
        status = random.randint(0, 1)
    if 'count' in request.cookies:
        count = int(request.cookies.get('count'))
    else:
        count = 0
    count = 1 + count
    if status==1:
        if count<3:
            resp = make_response(render_template("game/thanos.html",msg=u"很不幸，你被灭霸干掉了"))
        else:
            resp = make_response(render_template("game/thanos.html",msg=u"不要做无谓的努力了，你的死是为了更好的未来"))
    else:
        if count < 3:
            resp = make_response(render_template("game/thanos.html",msg=u"你从灭霸的手中侥幸逃脱了，可以看到明天的朝阳"))
        else:
            resp = make_response(render_template("game/thanos.html",msg=u"怎么，活着不开心，非要皮%d下？"%(count-2)))

    resp.set_cookie('status', str(status))
    resp.set_cookie('count', str(count))
    return resp
