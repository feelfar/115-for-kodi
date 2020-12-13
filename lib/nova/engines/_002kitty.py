# -*- coding: utf-8 -*-
#VERSION: 1.00

from helpers import retrieve_url, download_file
import json,urllib,re
from xbmcswift2 import Plugin

plugin = Plugin()
class kitty(object):
	url = 'https://cn.torrentkitty.tv'
	cookieurl=''
	name = 'kitty'
	support_sort=[];
	page_result_count=20;
	supported_categories = {'all': ''}
	

	def __init__(self):
		pageresult = retrieve_url(self.url,ignoreError='yes')
		match = re.search(r'action\s*\x3D\s*\x22(?P<cookieurl>.*?)\x22(?P<values>.*?)</form>', pageresult, re.DOTALL | re.IGNORECASE)
		if match:
			plugin.notify(match.group('cookieurl'))
			self.cookieurl =self.url+ match.group('cookieurl')+'?'
			
			for valuematch in re.finditer(r"(?si)name\s*\x3d\s*\x22(?P<name>.*?)\x22(?:\s+value\x3D\s*\x22\s*(?P<value>.*?)\x22)*", match.group("values"), re.DOTALL | re.IGNORECASE):
				if valuematch.group('value'):
					self.cookieurl += valuematch.group('name')+'='+valuematch.group('value')+'&'
				else:
					self.cookieurl += valuematch.group('name')+'=&'
		pass
	
	def search(self, what, cat='all',sorttype='-1',page=1):
		#plugin.notify(what)
		result={}
		result['state']=False
		result['list']=[]
		searchurl=self.url+'/search/%s/%s'%(what.encode('utf-8'),str(int(page)))
		try:
			courl=''
			pageresult = retrieve_url(self.url,ignoreError='yes')
			match = re.search(r'action\s*\x3D\s*\x22(?P<cookieurl>.*?)\x22(?P<values>.*?)</form>', pageresult, re.DOTALL | re.IGNORECASE)
			if match:
				plugin.notify(match.group('cookieurl'))
				courl =self.url+ match.group('cookieurl')+'?'
				
				for valuematch in re.finditer(r"(?si)name\s*\x3d\s*\x22(?P<name>.*?)\x22(?:\s+value\x3D\s*\x22\s*(?P<value>.*?)\x22)*", match.group("values"), re.DOTALL | re.IGNORECASE):
					if valuematch.group('value'):
						courl += valuematch.group('name')+'='+valuematch.group('value')+'&'
					else:
						courl += valuematch.group('name')+'=&'
			pageresult = retrieve_url(courl,referer=searchurl)
			#plugin.log.error(pageresult)

			#plugin.log.error(pageresult)
			rmain=r'<td class="name">(?P<title>.*?)</td><td class="size">(?P<filesize>.*?)</td><td class="date">(?P<createtime>.*?)</td>.*?<a href="(?P<magnet>magnet.*?)&tr='
			reobj = re.compile(rmain, re.DOTALL)
			for match in reobj.finditer(pageresult):
				title=match.group('title')
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				magnet=match.group('magnet')
				res_dict = dict()
				res_dict['name'] = title.encode('UTF-8')
				res_dict['size'] = '种子'+filesize
				res_dict['seeds'] = ''
				res_dict['leech'] = ''
				res_dict['link'] = magnet
				res_dict['date'] =createtime
				res_dict['desc_link'] = ''
				res_dict['engine_url'] = self.url
				result['list'].append(res_dict)
				
			if  pageresult.find('<a href="%s">%s</a>'%(str(int(page)+1),str(int(page)+1)))>0:
				result['nextpage']=True
		except:
			return result
		result['state']=True
		return result