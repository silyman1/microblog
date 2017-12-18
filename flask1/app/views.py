#-*- coding=utf-8 -*-
from app import app
from flask import render_template,flash,redirect
from .forms import LoginForm

import sys
reload(sys)
sys.setdefaultencoding('utf8')

@app.route('/')
@app.route('/index')
def index():
	user ={'nickname':'大大'}
	return render_template("index.html",user = user)
	
@app.route('/login',methods =['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('openid="'+form.openid.data+'",remember_me='+str(form.remember_me.data))
		return  redirect('index')
	return render_template('login.html',
						   title = '登录',
						   form = form,
						   providers = app.config['OPENID_PROVIDERS'])