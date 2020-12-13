# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url,download_file
import json,urllib,re


from xbmcswift2 import Plugin
plugin=Plugin()
class btdb(object):
	url = 'https://btdb.eu/'
	name = 'btdb'
	support_sort=['relevance','addtime','size','files','popular'];
	page_result_count=25;
	supported_categories = {'all': ''}
	
	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='relevance',page='1'):
		result={}
		result['state']=False
		result['list']=[]
		result['sorttype']=sorttype
		
		if sorttype=='addtime': sorttype='time'
		elif sorttype=='size': sorttype='size'
		elif sorttype=='files': sorttype='num_files'
		elif sorttype=='popular': sorttype='popular'
		else : sorttype=''

		
		searchurl=self.url+'?search=%s&page=%s&sort=%s'%(urllib.quote(what),str(int(page)),str(sorttype))
		#plugin.notify(searchurl)
		try:
			
			pageresult = retrieve_url(searchurl)
			#xbmc.log(msg=pageresult)
			rmain=r'item-title.*?title="(?P<title>.*?)">.*?href="(?P<magnet>magnet.*?)&.*?Size.*?">(?P<filesize>.*?)</span>.*?Files.*?">(?P<filecount>.*?)</span>.*?AddTime.*?">(?P<createtime>.*?)</span>'
			reobj = re.compile(rmain, re.DOTALL)
			for match in reobj.finditer(pageresult):
				title=match.group('title')
				
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				filecount=match.group('filecount')
				title=title.replace('<b>','').replace('</b>','')
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
			if pageresult.find('rel="next">Next')>=0:
				result['nextpage']=True
		except:
			return result
		
		result['state']=True
		return result