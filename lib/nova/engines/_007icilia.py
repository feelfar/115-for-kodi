# -*- coding: utf-8 -*-
#VERSION: 1.00


from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re

class icilia(object):
	url = 'http://icili.org'
	name = 'icili-a'
	support_sort=[];
	page_result_count=18;
	supported_categories = {'all': ''}

	def __init__(self):
		pass

	def download_torrent(self, info):
		print download_file(info, info)

	def search(self, what, cat='all',sorttype='seed',page='1'): 
		result={}
		result['state']=False
		result['list']=[]
		searchurl=self.url+'/a/list/%s/%s'%(urllib.quote(what),str(int(page)))
		try:
			pageresult = retrieve_url(searchurl)
			rmain=r'"title" href="(?P<href>.*?)">.*?"item-list">(?P<title>.*?)</div>.*?大小:<span>(?P<filesize>.*?)</span>.*?文件数:<span>(?P<filecount>.*?)</span>.*?创建日期:<span>(?P<createtime>.*?)</span>.*?热度:<span>(?P<heatlevel>.*?)</span>'
			reobj = re.compile(rmain, re.DOTALL)
			
			for match in reobj.finditer(pageresult):				
				title=match.group('title')
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				magnet=match.group('href')[match.group('href').rfind('/')+1:]			
				magnet='magnet:?xt=urn:btih:'+magnet
				if magnet:
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
			if  pageresult.find('>%s</a></li>'%(str(int(page)+1)))>0:
				result['nextpage']=True
		except:
			return result
		result['state']=True
		return result
	  