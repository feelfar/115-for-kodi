# -*- coding: utf-8 -*-
#VERSION: 1.00


from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re

class icili(object):
	url = 'http://www.2cili.com'
	name = '爱磁力'
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
		searchurl=self.url+'/list/%s/%s'%(urllib.quote(what),str(int(page)))
		try:
			pageresult = retrieve_url(searchurl)
			#xbmc.log(msg=pageresult)
			rmain=r'"title" href="/wiki/(?P<href>.*?)">(?P<title>.*?)</a>.*?收录时间.*?>(?P<createtime>.*?)<.*?活跃热度.*?>(?P<heatlevel>.*?)<.*?最后活跃.*?>(?P<lastdown>.*?)<.*?文件大小.*?>(?P<filesize>.*?)<'
			reobj = re.compile(rmain, re.DOTALL)
			
			for match in reobj.finditer(pageresult):				
				title=match.group('title')
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				title=title.replace('<span class="highlight">','').replace('</span>','')				
				# detialdata=retrieve_url(self.url+match.group('href'))		
				# detailreobj = re.compile(r'磁力链接：.*?href="(?P<magnet>.*?)">', re.DOTALL)		
				# detailmatch = detailreobj.search(detialdata)
				# if detailmatch:
					# magnet = detailmatch.group('magnet')			
				# else:
					# magnet = ''
				magnet='magnet:?xt=urn:btih:'+match.group('href')[0:40]
				
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
	  