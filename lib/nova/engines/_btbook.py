# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re,xbmc,xbmcgui
import urllib,urllib2
import cookielib

from xbmcswift2 import Plugin
plugin=Plugin()
class btbook(object):
	url = 'http://www.btmeet.org/search/'
	name = 'btbook'
	supported_categories = {'all': ''}

	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='-1',page='1'): 	
		result={}
		result['state']=False
		result['list']=[]
		
		if str(sorttype)=='-1':
			dialog = xbmcgui.Dialog()
			sorttype=dialog.select('btbook搜索-选择排序类型',['创建时间','文件大小','下载热度','相关度'])
			if sorttype==-1:
				return result
			sorttype=str(sorttype+1)
		result['sorttype']=sorttype
		searchurl=self.url+'%s/%s-%s.html'%(urllib.quote(what),str(int(page)),str(sorttype))
		#plugin.notify(searchurl)
		try:
			'''
			json_data = retrieve_url('http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=js')
			json_data= json_data.replace('\n','').replace('\r','')
			json_data=json_data[json_data.index('{'):json_data.index('}')+1]
			#xbmc.log(json_data)
			json_dict = json.loads(json_data)
			
			prov=json_dict['province']
			
			#声明一个CookieJar对象实例来保存cookie
			cookie = cookielib.CookieJar()
			#利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
			handler=urllib2.HTTPCookieProcessor(cookie)
			#通过handler来构建opener
			opener = urllib2.build_opener(handler)
			#此处的open方法同urllib2的urlopen方法，也可以传入request
			response = opener.open('http://www.btmilk.com/search/')
			cookie_item = cookielib.Cookie(
            version=0, name='prov', value=prov,
                     port=None, port_specified=None,
                     domain='http://www.btmilk.com/', domain_specified=None, domain_initial_dot=None,
                     path='/', path_specified=None,
                     secure=None,
                     expires=None,
                     discard=None,
                     comment=None,
                     comment_url=None,
                     rest=None,
                     rfc2109=False,
            )

			cookie.set_cookie(cookie_item)
			response = opener.open(searchurl)
			'''
			pageresult = retrieve_url(searchurl)
			#xbmc.log(pageresult)
			#pageresult=response.read()
			#xbmc.log(pageresult)
			rmain=r'创建时间.*?<b.*?>(?P<createtime>.*?)</b>.*?文件大小.*?<b.*?>(?P<filesize>.*?)</b>.*?下载热度.*?<b.*?>(?P<heatlevel>.*?)</b>.*?最近下载.*?<b.*?>(?P<lastdown>.*?)</b>.*?wiki/(?P<magnet>.*?).html.*?decodeURIComponent\x28"(?P<title>.*?)"\x29'
			reobj = re.compile(rmain, re.DOTALL)
			for match in reobj.finditer(pageresult):
				title=match.group('title').replace('"+"','')
				title=urllib.unquote(title)
				#title=urllib.urldecode(match.group('title').replace('"+"',''))
				#xbmc.log(title)
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				title=title.replace('<b>','').replace('</b>','')
				magnet=match.group('magnet')
				magnet='magnet:?xt=urn:btih:'+magnet
				res_dict = dict()
				res_dict['name'] = title
				res_dict['size'] = filesize
				res_dict['seeds'] = ''
				res_dict['leech'] = ''
				res_dict['link'] = magnet
				res_dict['date'] =createtime
				res_dict['desc_link'] = ''
				res_dict['engine_url'] = self.url
				result['list'].append(res_dict)
			if len(result['list'])>0:
				result['nextpage']=True
		except:
			return result
		
		result['state']=True
		return result