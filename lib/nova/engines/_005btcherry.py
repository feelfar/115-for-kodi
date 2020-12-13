# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re
from xbmcswift2 import Plugin
plugin=Plugin()
class btcherry(object):
	url = 'https://www.btcherries.org'
	name = 'btcherry'
	support_sort=['relevance','addtime','size','files','popular'];
	page_result_count=15;
	supported_categories = {'all': ''}

	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='relevance',page='1'): 	
		result={}
		result['state']=False
		result['list']=[]
		result['sorttype']=sorttype
		
		if sorttype=='addtime': sorttype='-time'
		elif sorttype=='size': sorttype='-size'
		elif sorttype=='files': sorttype='-filenums'
		elif sorttype=='popular': sorttype='-views'
		else : sorttype=''
		
		searchurl='%s/search/%s-%s%s.html'%(self.url,urllib.quote(what),str(int(page)),sorttype)
		#plugin.log.error(searchurl)
		try:
			pageresult = retrieve_url(searchurl)
			#plugin.log.error(pageresult)
			rmain=r'\x3Cdt\x3E.*?magnet\x2F(?P<magnet>.*?)\x2Ehtm.*?\x3E(?P<title>.*?)\x3C\x2Fa\x3E.*?收录日期\x3Cb\x3E(?P<createtime>.*?)\x3C\x2Fb.*?文件大小\x3Cb\x3E(?P<filesize>.*?)\x3C\x2Fb.*?文件数\x3Cb\x3E(?P<filecount>.*?)\x3C\x2Fb.*?下载次数\x3Cb\x3E(?P<pop>.*?)\x3C\x2Fb'
			reobj = re.compile(rmain, re.IGNORECASE | re.DOTALL)
			for match in reobj.finditer(pageresult):
				title=match.group('title')
				createtime=match.group('createtime')
				filesize=match.group('filesize')
				filecount=match.group('filecount')
				title = re.sub(r'<span\s+class="__cf_email.*?</span>', 'mail', title, re.IGNORECASE | re.DOTALL)
				title=title.replace('<b>','').replace('</b>','')
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
			if len(result['list'])>0:
				result['nextpage']=True
		except:
			return result
		
		result['state']=True
		return result