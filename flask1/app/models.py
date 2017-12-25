#-*- coding=utf-8 -*-
from app import db,app
from hashlib import md5
import sys
import sys
if sys.version_info >= (3, 0):
	enable_search = False
else:
	enable_search = True
	import flask.ext.whooshalchemy as whooshalchemy

followers =db.Table('followers',
	db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
class User(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	nickname = db.Column(db.String(64),index= True,unique=True)
	email = db.Column(db.String(120),index= True,unique=True)#对字段修改migrate好像无效
	posts = db.relationship('Post',backref='author',lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)
	fav = db.Column(db.String(64))
	followed =db.relationship('User',
							secondary = followers,
							primaryjoin = (followers.c.follower_id == id),
							secondaryjoin = (followers.c.followed_id == id),
							backref =db.backref('followers',lazy ='dynamic'),
							lazy='dynamic')
	def follow(self,user):
		if not self.is_following(user):
			self.followed.append(user)
			return self
	def unfollow(self,user):
		if self.is_following(user):
			self.followed.remove(user)
			return self
	def is_following(self,user):
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0
	def followed_posts(self):
		return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())
	@staticmethod
	def make_unique_nickname(nickname):
		if User.query.filter_by(nickname = nickname).first() == None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query.filter_by(nickname = new_nickname).first() == None:
				break
			version += 1
		return new_nickname
	def avatar(self, size):
		return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)
	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.id)	 # python 2
		except NameError:
			return str(self.id)	 # python 3
	def __repr__(self):
		return '<User %r>'%(self.nickname)
class Post(db.Model):
	__searchable__ = ['body']
	id = db.Column(db.Integer,primary_key =True)
	body = db.Column(db.String(140))
	timestamp =db.Column(db.DateTime)
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	mark = db.Column(db.Integer)#设为隐私标记，仅自己可见
	review = db.relationship('Comment', backref='post', lazy='dynamic')
	def post_comments(self):
		return self.review.order_by(Comment.timestamp.desc())
	def __repr__(self):
		return '<Post %r>'% (self.body)
class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	observer = db.Column(db.String(64),index= True)
	comment_id = db.Column(db.Integer, db.ForeignKey('post.id'))
	content = db.Column(db.String(140))  # 评论功能
	timestamp = db.Column(db.DateTime)
	def __repr__(self):
		return '<Comment %r>'% (self.content)
if enable_search:
	whooshalchemy.whoosh_index(app,Post)
