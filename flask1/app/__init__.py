#-*- coding=utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os 
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'  #让flask_login知道哪个视图允许用户登录
oid = OpenID(app,os.path.join(basedir,'tmp'))
from app import views,models
from momentjs import momentjs
app.jinja_env.globals['momentjs'] = momentjs