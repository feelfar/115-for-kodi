# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re,xbmc,xbmcgui

from xbmcswift2 import Plugin
plugin=Plugin()
class btkiss(object):
	url = 'http://www.btkiss.net/list/'
	name = 'btkiss'
	supported_categories = {'all': ''}

	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='-1',page='1'): 	
		result={}
		result['state']=False
		result['list']=[]
		
		if str(sorttype)=='-1':
			dialog = xbmcgui.Dialog()
			sorttype=dialog.select('btkiss搜索-选择排序类型',['创建时间','文件大小','相关度'])
			if sorttype==-1:
				return result
			sorttype=str(sorttype+1)
		result['sorttype']=sorttype
		searchurl=self.url+'%s-hd%s-%s.html'%(urllib.quote(what),str(sorttype),str(int(page)))
		#plugin.notify(searchurl)
		try:
			pageresult = retrieve_url(searchurl)
			#xbmc.log(msg=pageresult)
			rmain=r'<a title="(?P<title>.*?)" target="_blank".*?<dl class="BotInfo">(?P<filelist>.*?)<dt>创建时间：<span>(?P<createtime>.*?)</span>.*?文件数：<span>(?P<filecount>.*?)</span>.*?文件大小：<span>(?P<filesize>.*?)</span>.*?下载热度：<span>(?P<heatlevel>.*?)</span>.*?最近下载：<span>(?P<lastdown>.*?)</span>.*?href="(?P<magnet>.*?)"'
			reobj = re.compile(rmain, re.DOTALL)
			for match in reobj.finditer(pageresult):
				title=match.group('title')
				#plugin.notify(title)
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				title=title.replace('<b>','').replace('</b>','')
				magnet=match.group('magnet')
				
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
			if pageresult.find('">下一页</a>')>=0:
				result['nextpage']=True
		except:
			return result
		
		result['state']=True
		return result