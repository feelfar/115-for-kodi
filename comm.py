# -*- coding: utf-8 -*-
# comm.py
import xbmc,sys,json,urllib2,gzip,time,os
import httplib, ssl
import socket
import HTMLParser

from StringIO import StringIO
from zhcnkbd import Keyboard

__cwd__=os.path.dirname(__file__)
__lib__  = xbmc.translatePath( os.path.join( __cwd__, 'lib' ) )
sys.path.append (__lib__)
sys.path.append (xbmc.translatePath( os.path.join(__lib__,'nova') ))

from xbmcswift2 import Plugin
plugin = Plugin()
setthumbnail=plugin.get_storage('setthumbnail')
setthumbnail['set']=False

moviepoint=plugin.get_storage('moviepoint')
searchvalues=plugin.get_storage('searchvalues')

colors = {'dir': 'FF9966','video': 'FF0033','bt': '33FF00', 'audio': '66CCCC', 'subtitle':'505050', 'image': '99CC33',
		'back': '0099CC','next':'CCCCFF', 'menu':'CCFF66', 'star1':'FFFF00','star0':'777777','sort':'666699','filter':'0099CC',
		'-1':'FF0000','0':'8B4513','1':'CCCCFF','2':'7FFF00'}

ALL_VIEW_CODES = {
	'list': {
		'skin.confluence': 50, # List
		'skin.estuary': 50, # List
		'skin.aeon.nox': 50, # List
		'skin.droid': 50, # List
		'skin.quartz': 50, # List
		'skin.re-touched': 50, # List
	},
	'thumbnail': {
		'skin.confluence': 500, # Thumbnail
		'skin.estuary': 500, # Thumbnail
		'skin.estouchy': 500, # Thumbnail
		'skin.aeon.nox': 500, # Wall
		'skin.droid': 51, # Big icons
		'skin.quartz': 51, # Big icons
		'skin.re-touched': 500, #re-touched
		'skin.confluence-vertical': 500,
		'skin.jx720': 52,
		'skin.pm3-hd': 53,
		'skin.rapier': 50,
		'skin.simplicity': 500,
		'skin.slik': 53,
		'skin.touched': 500,
		'skin.transparency': 53,
		'skin.xeebo': 55,
	},
}

def colorize_label(label, _class=None, color=None):
	color = color or colors.get(_class)

	if not color:
		return label

	if len(color) == 6:
		color = 'FF' + color

	return '[COLOR %s]%s[/COLOR]' % (color, label)

def get_installedversion():
	# retrieve current installed version
	json_query = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
	json_query = unicode(json_query, 'utf-8', errors='ignore')
	json_query = json.loads(json_query)
	version=14
	if json_query.has_key('result') and json_query['result'].has_key('version'):
		version=int(json_query['result']['version']['major'])
	return version
version=get_installedversion()

def keyboard(title=u'请输入搜索关键字',text=''):
	buildinkb=False
	if str(plugin.get_setting('buildinkb'))=='true' or int(version)<16:
		buildinkb=True
	if buildinkb:
		kb = Keyboard(text,title)
	else:
		kb=xbmc.Keyboard(text,title)
	kb.doModal()
	text=''
	if kb.isConfirmed():
		text=kb.getText()
	return text

class MyRedirectHandler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		setcookie = str(headers["Set-Cookie"])
		req.add_header("Cookie", setcookie)
		return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

def _http(url, data=None,referer=None,cookie=None):
	#url=url.encode('UTF-8')
	request=''
	for i in range(1,5):
		try:
			req = urllib2.Request(url)
			req.add_header('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)')
			req.add_header('Accept-encoding', 'gzip,deflate')
			req.add_header('Accept-Language', 'zh-cn')
			if cookie:
				req.add_header('Cookie', cookie)
			if referer:
				req.add_header('Referer', referer)
			opener = urllib2.build_opener(MyRedirectHandler)
			if data:
				#data=data.encode('UTF-8')
				rsp = opener.open(req, data=data, timeout=15)
			else:
				rsp = opener.open(req, timeout=15)
			
			if rsp.info().get('Content-Encoding') == 'gzip':
				request = gzip.GzipFile(fileobj=StringIO(rsp.read())).read()
			else:
				request = rsp.read()
			if 'Set-Cookie' in rsp.headers:
				request='Set_Cookie:'+rsp.headers['Set-Cookie']+'\r'+request
			rsp.close()
			#html_parser=HTMLParser.HTMLParser()
			#request=html_parser.unescape(request)
			break
		except Exception,e:
			time.sleep(1)
			plugin.log.error(str(e))
	
	return request

def url_is_alive(url):
	request = urllib2.Request(url)
	request.get_method = lambda : 'HEAD'
	try:
		response = urllib2.urlopen(request)
		return True
	except:
		return False

@plugin.route('/showpic/<imageurl>')
def showpic(imageurl):
	xbmc.executebuiltin("ShowPicture(%s)" % (imageurl))
	return

@plugin.route('/shellopenurl/<url>/<samsung>')
def shellopenurl(url,samsung):
	osWin = xbmc.getCondVisibility('system.platform.windows')
	osOsx = xbmc.getCondVisibility('system.platform.osx')
	osLinux = xbmc.getCondVisibility('system.platform.linux')
	osAndroid = xbmc.getCondVisibility('System.Platform.Android')
	if osOsx:    
		# ___ Open the url with the default web browser
		xbmc.executebuiltin("System.Exec(open "+url+")")
	elif osWin:
		# ___ Open the url with the default web browser
		xbmc.executebuiltin("System.Exec("+url+")")
	elif osLinux and not osAndroid:
		# ___ Need the xdk-utils package
		xbmc.executebuiltin("System.Exec(xdg-open "+url+")") 
	elif osAndroid:
		androidbrowser='com.android.browser'
		if str(samsung)=='1':
			androidbrowser='com.samsung.vrvideo'
		# ___ Open media with standard android web browser
		xbmc.executebuiltin('StartAndroidActivity(%s,android.intent.action.VIEW,,%s)'%(androidbrowser,url))
	
