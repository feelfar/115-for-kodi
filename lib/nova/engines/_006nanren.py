# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url,download_file
import json,urllib,re,HTMLParser

from xbmcswift2 import Plugin
plugin=Plugin()

class nanren(object):
	url = 'http://nanrencili.bid/list/'
	name = 'nanren'
	support_sort=['relevance','addtime','size','files','popular'];
	page_result_count=10;
	supported_categories = {'all': ''}
	
	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='relevance',page='1'):
		result={}
		result['state']=False
		result['list']=[]
		result['sorttype']=sorttype
		
		if sorttype=='addtime': sorttype='2'
		elif sorttype=='size': sorttype='1'
		elif sorttype=='files': sorttype='5'
		elif sorttype=='popular': sorttype='3'
		else : sorttype='0'

		searchurl=self.url+'%s/%s/%s/2.html'%(urllib.quote(what),str(int(page)),str(sorttype))
		#plugin.notify(searchurl)
		try:
			pageresult = retrieve_url(searchurl)
			#pageresult=html_parser.unescape(pageresult)
			#plugin.log.error(pageresult)
			#xbmc.log(msg=pageresult)
			rmain=r'"detail">.*?target="_blank">(?P<title>.*?)\x2etorrent.*?<span>收录时间:<b>(?P<createtime>.*?)</b></span>.*?<span>文档个数:<b>(?P<filecount>.*?)</b>.*?<span>文档大小:<b>(?P<filesize>.*?)</b></span>.*?<span>人气:<b>(?P<seeds>.*?)</b></span>.*?href="(?P<magnet>.*?)"'
			reobj = re.compile(rmain, re.DOTALL)
			for match in reobj.finditer(pageresult):
				title=match.group('title')
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				filecount=match.group('filecount')
				
				title = re.sub(r'<span\s+class="__cf_email.*?</span>', '', title, re.IGNORECASE | re.DOTALL)
				title=title.replace('<span class="red">','').replace('</span>','')

				magnet=match.group('magnet')
				
				res_dict = dict()
				res_dict['name'] = title
				res_dict['size'] = filesize
				res_dict['filecount'] = filecount
				res_dict['seeds'] = ''
				res_dict['leech'] = ''
				res_dict['link'] = magnet
				res_dict['date'] =createtime
				res_dict['desc_link'] = ''
				res_dict['engine_url'] = self.url
				result['list'].append(res_dict)
			if pageresult.find('>下一页</a>')>=0:
				result['nextpage']=True
		except Exception,ex:
			plugin.log.error('006nanrenerror:'+str(ex))
			return result
		
		result['state']=True
		return result