# -*- coding: utf-8 -*-
#VERSION: 1.00


from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re

class bt2mag(object):
	url = 'https://tellme.pw/btsow'
	name = 'bt2mag'
	support_sort=[];
	page_result_count=30;
	supported_categories = {'all': ''}

	def __init__(self):
		pass

	def download_torrent(self, info):
		print download_file(info, info)

	def search(self, what, cat='all',sorttype='relevance',page='1'): 
	
		result={}
		result['state']=False
		result['list']=[]
		
		
		try:
			#searchurl='https://btsow.pw'
			pageresult = retrieve_url(self.url)
			match = re.search(r'<strong><a\x20href="(.*?)"', pageresult, re.DOTALL | re.MULTILINE)
			if match:
				searchurl = match.group(1)
			
			
			searchurl=searchurl+'/search/%s/page/%s'%(urllib.quote(what),str(int(page)))

			pageresult = retrieve_url(searchurl)
			#xbmc.log(msg=pageresult)
			rmain=r'<div\x20class="row">.*?<a\x20href="(?P<href>.*?)"\x20title="(?P<title>.*?)">.*?Size:(?P<filesize>.*?)\x20/\x20Convert\x20Date:(?P<createtime>.*?)</div>'
			reobj = re.compile(rmain, re.DOTALL)
			
			for match in reobj.finditer(pageresult):				
				title=match.group('title')
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				magnet=match.group('href')[match.group('href').rfind('/')+1:]			
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
	  