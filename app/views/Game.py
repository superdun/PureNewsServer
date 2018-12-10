# -*- coding:utf-8 -*-
import random

from  flask import Blueprint, request, render_template, make_response,jsonify

game = Blueprint('game', __name__)


@game.route('/liuzi')
def Liuzi():
    return render_template("game/liuzi.html")
@game.route('/gufeng')
def Gufeng():
    return render_template("game/GufengWeb.html")
@game.route('/api/gufeng')
def GufengAPI():
    two1={
    'two_a' : u"梨花 桃花 朱砂 白发 天下 落花 烟花 杀伐 人家 韶华 风华 繁华".split(" "),
    'two_an' : u"血染 墨染 断弦 散乱 轻叹 长安 江南 忘川 千年 纸伞 红颜 红线 黄泉".split(" "),
    'two_eng' : u"倾城 孤城 空城 旧城 心疼 春风 一生 三生 浮生".split(" "),
    'two_i' : u"白衣 素衣 嫁衣 迷离 公子 红衣".split(" "),
    'two_ang' : u"情殇 爱殇 剑殇 灼殇 仓皇 匆忙 陌上 焚香 墨香 微凉 断肠 痴狂 凄凉 黄梁 未央 成双 无恙 虚妄 凝霜 洛阳".split(" "),
    }
    two2 = u"旧人 伊人 红尘 奈何 陌路 白骨 黄土 乱世 青丝 青史 笑靥 浅笑 明眸 回眸 红豆 白首 烟火 碧落 紫陌 烟雨 青冢".split(" ")



    four1=u"情深缘浅 如花美眷 似水流年 曲终人散 一世长安 ".split(" ")
    four2=u"情深不寿 阴阳相隔 眉目如画 繁华落尽 莫失莫忘 不诉离殇 ".split(" ")


    types = {u"XX，XX，XX了XX":(3,3,2,20),
    u"XX，XX，不过是一场XX":(2,2,4,40),
    u"你说XX， 我说XX，最后不过XX":(2,2,4,40),
    u"XX，XX，许我一场XX":(3,2,2,40),
    u"你说XX，XX，后来XX XX":(2,3,4,40),
    u"XX，XX，终不敌XX":(2,2,4,40)}
    import random
    typeKeys = types.keys()
    typeKey = random.randint(0,len(types)-1)
    typeVal = types[typeKeys[typeKey]]
    resultList= []
    resultMid = []
    resultEnd = []
    result = ""
    if typeVal[2] == 2:
        randomResult = random.sample(range(0, len(two2)-1), typeVal[1]*typeVal[0])
        for i in randomResult:
            resultMid.append(two2[i])
    if typeVal[2] == 4:
        randomResult = random.sample(range(0, len(four2)-1), typeVal[1]*typeVal[0])
        for i in randomResult:
            resultMid.append(four2[i])
    if typeVal[3] == 20:
        rk = random.randint(0,len(two1.keys())-1)
        randomResult = random.sample(range(0, len(two1[two1.keys()[rk]])-1), typeVal[0])
        for i in randomResult:
            resultEnd.append(two1[two1.keys()[rk]][i])
    if typeVal[3] == 40:
        randomResult = random.sample(range(0, len(four1)-1), typeVal[0])
        for i in randomResult:
            resultEnd.append(four1[i])

    for j in range(typeVal[0]):
        r = typeKeys[typeKey]
        count = 0
        while "XX" in r:
            if count==typeVal[1]:
                r = r.replace("XX",resultEnd.pop(0),1 )
            else:
                r = r.replace("XX", resultMid.pop(0), 1)
            count= count+1
        result = result+"\n"+r

    return jsonify({"result":result})