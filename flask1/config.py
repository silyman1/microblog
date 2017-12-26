#-*- coding=utf-8 -*-
import os 

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


CSRF_ENABLED = True


SECRET_KEY = 'abcdefg'


OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
	
# pagination
POSTS_PER_PAGE = 8
#...
DEFAULT_BACKGROUND = '444.jpg'
DEFAULT_AVATAR = '/static/img/001.jpg'
#全文搜索数据库
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50
#comment
COMMENTS_PER_PAGE = 4

avatar_urls =  {'A01':'/static/img/dynamic2.gif',
				'A02':'/static/img/dynamic3.gif',
				'A03':'/static/img/pig2.gif',
				'A04':'/static/img/pig5.jpg',
				'A05':'/static/img/pig4.jpg',
				'A06':'/static/img/pig3.jpg',
				'A07':'/static/img/pig1.jpg',
}