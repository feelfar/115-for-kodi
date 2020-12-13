# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url,download_file
import json,urllib,re

from xbmcswift2 import Plugin
plugin=Plugin()
class btfuli(object):
	url = 'http://btfuliziyuan.cc'
	name = 'btfuli'
	support_sort=['relevance','addtime','size','files','popular'];
	page_result_count=20;
	supported_categories = {'all': ''}
	
	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='relevance',page='1'):
		result={}
		result['state']=False
		result['list']=[]
		result['sorttype']=sorttype
		
		if sorttype=='addtime': sorttype='1'
		elif sorttype=='size': sorttype='2'
		elif sorttype=='files': sorttype='3'
		elif sorttype=='popular': sorttype='4'
		else : sorttype='0'
		searchurl='%s/find/%s/%s-0/%s.jsp'%(self.url,urllib.quote(what),str(sorttype),str(int(page)))
		#plugin.notify(searchurl)
		try:
			pageresult = retrieve_url(searchurl)
			
			#plugin.log.error(pageresult)
			rmain=r'<dl\s+.*?target=[\x22\x27]_blank[\x22\x27]>(?P<title>.*?)</a></dt>.*?收录时间:<b>(?P<createtime>.*?)</b>.*?<span>文件大小:<b>(?P<filesize>.*?)</b>.*?<span>文件数:<b>(?P<filecount>.*?)</b>.*?<span>人气:<b>(?P<popular>.*?)</b>.*?href=[\x22\x27](?P<magnet>.*?)[\x22\x27].*?</dl>'
			reobj = re.compile(rmain, re.IGNORECASE | re.DOTALL)
			for match in reobj.finditer(pageresult):
				
				title=match.group('title')
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				filecount=match.group('filecount')
				title = re.sub(r'<span\s+class="__cf_email.*?</span>', 'mail', title, re.IGNORECASE | re.DOTALL)
				title=title.replace('<b>','').replace('</b>','')
				magnet=self.url+match.group('magnet')
				
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
				plugin.log.error(title)
				result['list'].append(res_dict)
			if pageresult.find('>»</a>')>=0:
				result['nextpage']=True
		except Exception,ex:
			plugin.log.error(name+' 失败'+str(ex))
			return result
		
		result['state']=True
		return result