# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re
from xbmcswift2 import Plugin
plugin=Plugin()

class lemoncili(object):
	url = 'https://lemoncili.com'
	name = 'lemoncili'
	support_sort=['relevance','addtime','size','files','popular'];
	page_result_count=0;
	supported_categories = {'all': ''}

	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='relevance',page='1'): 
		result={}
		result['state']=False
		result['list']=[]
		result['sorttype']=sorttype
		result['nextpage']=True
		
		if sorttype=='addtime': sorttype='date'
		elif sorttype=='size': sorttype='length'
		elif sorttype=='files': sorttype='filenum'
		else : sorttype='relevance'
		plugin.notify(str(self.page_result_count))
		curpage=0
		while result['nextpage']==True and curpage*10<self.page_result_count:
			curpage+=1
			searchurl='%s/search?keyword=%s&s=%s&p=%s'%(self.url,urllib.quote(what),sorttype,str(curpage))
			#plugin.log.error(searchurl)
			try:
				pageresult = retrieve_url(searchurl)
				#plugin.log.error(pageresult)
				rmain=r'\x2Fdetail\x2F[0-9a-f]{5}\x2F(?P<magnet>.*?)\x22.*?title\x3D\x22(?P<title>.*?)\x22.*?文件大小[:：]?\s*\x3Cspan\x3E(?P<filesize>.*?)\x3C.*?文件数量[:：]?\s*\x3Cspan\x3E(?P<filecount>.*?)\x3C.*?收录时间[:：]?\s*\x3Cspan\x3E(?P<createtime>.*?)\x3C'
				reobj = re.compile(rmain, re.IGNORECASE | re.DOTALL)
				
				for match in reobj.finditer(pageresult):
					title=match.group('title')
					createtime=match.group('createtime')
					filesize=match.group('filesize')
					filecount=match.group('filecount')
					magnet=r'magnet:?xt=urn:btih:'+match.group('magnet')
					
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
					
				if  pageresult.find(r';p='+str(int(page)+1))>=0:
					result['nextpage']=True
			except Exception,ex:
				plugin.log.error(name+' 失败'+str(ex))
				return result
		
		result['state']=True
		return result