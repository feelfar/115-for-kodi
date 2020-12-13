# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url,download_file
import json,urllib,re

from xbmcswift2 import Plugin
plugin=Plugin()
class magnetdl(object):
	url = 'https://www.magnetdl.me'
	name = 'magnetdl'
	support_sort=['popular','addtime','size','files'];
	page_result_count=50;
	supported_categories = {'all': ''}
	
	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='popular',page='1'):
		result={}
		result['state']=False
		result['list']=[]
		result['sorttype']=sorttype
		
		if sorttype=='addtime': sorttype='age'
		elif sorttype=='size': sorttype='size'
		elif sorttype=='files': sorttype='files'
		else : sorttype='se'
		
		searchurl='%s/search/%s/%s/desc/%s/'%(self.url,urllib.quote(what),str(sorttype),str(int(page)))
		#plugin.notify(searchurl)
		try:
			pageresult = retrieve_url(searchurl)
			
			#plugin.log.error(pageresult)
			rmain=r'a\s+href\x3D[\x22\x27](?P<magnet>magnet.*?)[\x22\x27].*?Direct\s+Download.*?title\x3D[\x22\x27](?P<title>.*?)[\x22\x27].*?\x3Ctd\x3E(?P<createtime>.*?)\x3C\x2Ftd\x3E.*?\x3Ctd\x3E(?P<filecount>.*?)\x3C\x2Ftd\x3E.*?\x3Ctd\x3E(?P<filesize>.*?)\x3C\x2Ftd\x3E'
			reobj = re.compile(rmain, re.IGNORECASE | re.DOTALL)
			for match in reobj.finditer(pageresult):
				
				title=match.group('title')
				filesize=match.group('filesize')
				filecount=match.group('filecount')
				createtime=match.group('createtime')
				
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
				plugin.log.error(title)
				result['list'].append(res_dict)
			if pageresult.find('.././%s/">Next Page'%(str(int(page)+1)))>=0:
				result['nextpage']=True
		except Exception,ex:
			plugin.log.error(name+' 失败'+str(ex))
			return result
		
		result['state']=True
		return result