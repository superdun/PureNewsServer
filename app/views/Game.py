# -*- coding:utf-8 -*-
import random

from  flask import Blueprint, request, render_template, make_response

game = Blueprint('game', __name__)


@game.route('/liuzi')
def Liuzi():
    return render_template("game/liuzi.html")
