#-*- coding=utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Length
from app.models import User
class LoginForm(Form):
	openid = StringField('openid',validators=[DataRequired()])
	remember_me = BooleanField('remember_me',default=False)
class EditForm(Form):
	nickname = StringField('nickname',validators=[DataRequired()])
	about_me = TextAreaField('about_me',validators=[Length(min=0,max=140)])
	email = StringField('email',validators=[DataRequired()])
	def __init__(self,original_nickname,original_email,*args,**kwargs):
		Form.__init__(self,*args,**kwargs)
		self.original_nickname = original_nickname
		self.original_email = original_email
	def validate(self):
		user = User.query.filter_by(nickname=self.nickname.data).first()
		email =User.query.filter_by(email =self.email.data).first()
		if not Form.validate(self):
			return False
		if self.nickname.data == self.original_nickname:
			if self.email.data== self.original_email:
				print 'ok5'
				return True
			else:
				if email != None:
					print 'ok4444'
					self.email.errors.append('此邮箱已被使用！！！')
					return  False
				else:
					print 'ok'
					return True
		if user != None:
			print 'ok2'
			self.nickname.errors.append('此昵称已被使用!!!')
			return False
		print 'ok3'
		return True
class PostForm(Form):
	post = StringField('post',validators=[DataRequired()])
class SearchForm(Form):
	search = StringField('search', validators=[DataRequired()])
class CommentForm(Form):
	comment = StringField('comment', validators=[DataRequired()])