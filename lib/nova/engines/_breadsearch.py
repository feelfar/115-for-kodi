# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re,xbmc,xbmcgui

from xbmcswift2 import Plugin
plugin=Plugin()
class breadsearch(object):
	url = 'http://breadsearch.com/search/'
	name = 'breadsearch'
	supported_categories = {'all': ''}

	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='-1',page='1'): 	
		result={}
		result['state']=False
		result['list']=[]
		searchurl=self.url+'%s/%s'%(urllib.quote(what),str(int(page)))
		#plugin.notify(searchurl)
		try:
			pageresult = retrieve_url(searchurl)
			#xbmc.log(msg=pageresult)
			rmain=r'target="_blank">(?P<title>.*?)</a></span>.*?收录时间.*?value">(?P<createtime>.*?)</span>.*?大小.*?value">(?P<filesize>.*?)</span>.*?文件数.*?value">(?P<filecount>.*?)</span>.*?href="(?P<magnet>.*?)">磁力链接'
			reobj = re.compile(rmain, re.DOTALL)
			for match in reobj.finditer(pageresult):
				title=match.group('title')
				#plugin.notify(title)
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				title=title.replace("<span class='highlight'>","").replace('</span>','')
				filecount=match.group('filecount')
				filesize=filesize.replace('&nbsp;',' ')
				createtime=createtime.replace('&nbsp;',' ')
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
			if len(result['list'])>0:
				result['nextpage']=True
		except:
			return result
		
		result['state']=True
		return result