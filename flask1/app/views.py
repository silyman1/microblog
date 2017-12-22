#-*- coding=utf-8 -*-
from app import app,db,lm,oid
from flask import render_template,flash,redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from .forms import LoginForm,EditForm,PostForm,SearchForm,CommentForm
from .models import User,Post,Comment
import sys
import time
from datetime import datetime
from config import POSTS_PER_PAGE,COMMENTS_PER_PAGE
reload(sys)
sys.setdefaultencoding('utf8')
@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()
		g.search_form = SearchForm()
		g.form2 = CommentForm()
@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page=1):
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data,timestamp=datetime.utcnow(),author=g.user,mark=0)
		db.session.add(post)
		db.session.commit()
		flash("发表成功~~")
		return redirect(url_for('index'))#避免了用户在提交 blog 后不小心触发刷新的动作而导致插入重复的 blog。
	posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
	return render_template("index.html",form= form,title='我的主页',posts=posts)
	
@app.route('/login',methods =['GET','POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
	return render_template('login.html',
						   title = '登录',
						   form = form,
						   providers = app.config['OPENID_PROVIDERS'])
@oid.after_login
def after_login(resp):
	if resp.email is None or resp.email =='':
		flash('email不能为空，请重新登录')
		return redirect(url_for('login'))
	user =User.query.filter_by(email=resp.email).first()#user =User.query.filter_by(nickname =resp.nickname).first()
	if user is None:
		nickname = resp.nickname
		if nickname is None or nickname == '':
			flash('昵称不能为空，请重新登录')
			return redirect(url_for('login'))
		nickname = User.make_unique_nickname(nickname)
		user = User(nickname=nickname,email=resp.email)
		db.session.add(user)
		db.session.commit()
		db.session.add(user.follow(user))     #关注自己
		db.session.commit()
	remember_me = False
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))
@lm.user_loader
def load_user(id):
	return User.query.get(int(id))
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))
@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname,page=1):
	user = User.query.filter_by(nickname=nickname).first()
	if user == None:
		flash('用户:'+nickname+'未找到！！')
		return redirect(url_for('index'))
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
	return render_template('user.html',
							user=user,
							title='个人信息页',
							posts=posts)
@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.nickname,g.user.email)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		g.user.email = form.email.data
		db.session.add(g.user)
		db.session.commit()
		flash('信息修改成功！')
		return redirect(url_for('user',nickname=g.user.nickname))
	else:
		form.nickname.data =g.user.nickname
		form.about_me.data=g.user.about_me
		form.email.data = g.user.email
	return render_template('edit.html',form=form,title = '修改个人信息')
@app.errorhandler(404)
def internal_error(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('500.html'), 500
@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
	user = User.query.filter_by(nickname = nickname).first()
	if user is None:
		flash('%s 为未知用户'%nickname)
		return redirect(url_for('index'))
	if user == g.user:
		flash('不能关注自己!')
		return redirect(url_for('user', nickname=nickname))
	u = g.user.follow(user)
	if u is None:
		flash('关注 %s 失败'% nickname)
		return redirect(url_for('user', nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash('关注 %s 成功！！！ '%nickname)
	return redirect(url_for('user', nickname=nickname))
@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
	user = User.query.filter_by(nickname = nickname).first()
	if user is None:
		flash('%s 为未知用户'%nickname)
		return redirect(url_for('index'))
	if user == g.user:
		flash('不能取消关注自己!')
		return redirect(url_for('user', nickname=nickname))
	u = g.user.unfollow(user)
	if u is None:
		flash('取消关注 %s 失败'% nickname)
		return redirect(url_for('user', nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash('取消关注 %s 成功！！！ '%nickname)
	return redirect(url_for('user', nickname=nickname))
@app.route('/search',methods=['POST'])
@login_required
def search():
	if not g.search_form.validate_on_submit():
		return redirect(url_for('index'))
	return redirect(url_for('search_results',query=g.search_form.search.data))

from config import MAX_SEARCH_RESULTS
@app.route('/search_results/<query>')
@login_required
def search_results(query):
	results = Post.query.whoosh_search(query,MAX_SEARCH_RESULTS).all()
	return render_template('search_results.html',
							query=query,
							title= '查询结果',
							results =results)
@app.route('/delete/<int:id>')
@login_required
def delete(id):
	post = Post.query.get(id)
	if post == None:
		flash('找不到要删除的内容。')
		return redirect(url_for('index'))
	if post.author.id !=g.user.id:
		flash('无法删除此内容')
		return redirect(url_for('index'))
	db.session.delete(post)
	db.session.commit()
	flash('删除成功！！！')
	return redirect(url_for('index'))
@app.route('/mark/<int:id>')
@login_required
def mark(id):
	post = Post.query.get(id)
	if post.mark == 0:
		post.mark =1
		db.session.add(post)
		db.session.commit()
		flash('成功设为隐私！！')
		return redirect(url_for('user',nickname=g.user.nickname))
	if post.mark == 1:
		post.mark =0
		db.session.add(post)
		db.session.commit()
		flash('已将此内容设为公开！！')
		return redirect(url_for('user',nickname=g.user.nickname))
@app.route('/comment/<int:id>',methods =['GET','POST'])
@login_required
def comment(id):
	post = Post.query.filter_by(id=id).first()
	if g.form2.validate_on_submit():
		print g.user.nickname
		comment = Comment(content=g.form2.comment.data,timestamp=datetime.utcnow(),post=post,observer=g.user.nickname)
		db.session.add(comment)
		db.session.commit()
		flash("评论成功~~")
		return redirect(url_for('index'))
	flash("评论失败~~")
	return redirect(url_for('index'))
@app.route('/delete_c/<int:id>')
@login_required
def delete_c(id):
	comment = Comment.query.get(id)
	if comment == None:
		flash('找不到要删除的评论。')
		return redirect(url_for('index'))
	if comment.post.user_id !=g.user.id:
		flash('无法删除此内容')
		return redirect(url_for('index'))
	db.session.delete(comment)
	db.session.commit()
	flash('删除评论成功！！！')
	return redirect(url_for('index'))