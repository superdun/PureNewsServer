# coding=utf-8
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
import flask_login
import flask_restless
import datetime

db = SQLAlchemy()
admin = Admin()
login_manager = flask_login.LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('localConfig.py')


    db.init_app(app)
    db.app = app



    login_manager.init_app(app)

    from  models.dbORM import User as U
    def getusers():
        users = {}
        raw_users = U.query.all()

        for user in raw_users:
            users[user.name] = {'password': user.password, 'username': user.name,
                                'id': user.id}
        return users

    class User(flask_login.UserMixin):
        pass
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return render_template("login.html")

    @login_manager.user_loader
    def user_loader(username):
        users = getusers()
        if username not in users:
            return

        user = User()
        user.name = username
        user.id = users[username]['id']
        return user

    @login_manager.request_loader
    def request_loader(request):
        users = getusers()

        username = request.form.get('username')
        password = request.form.get('password')
        if password == "":
            return
        if username not in users:
            return

        user = User()
        user.name = username
        user.id = users[username]['id']
        db.session.commit()
        # DO NOT ever store passwords in plaintext and always compare password
        # hashes using constant-time comparison!

        user.is_authenticated = request.form[
                                    'password'] == users[username]['password']

        return user

    # 注册蓝本
    from views import Login,Api,Web
    from models.dbORM import Post
    app.register_blueprint(Api.api, url_prefix='')
    app.register_blueprint(Login.login_bp, url_prefix='')
    app.register_blueprint(Web.web, url_prefix='')
    manager = flask_restless.APIManager(app,flask_sqlalchemy_db=db)
    manager.create_api(Post, methods=['GET'])
    # 附加路由和自定义的错误页面
    with app.app_context():
        from modules.Admin import dashboard

        dashboard()


    return app