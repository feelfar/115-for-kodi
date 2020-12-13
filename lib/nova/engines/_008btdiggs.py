# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url,urlgetlocation
import json,urllib,re,xbmc,time

from xbmcswift2 import Plugin
plugin=Plugin()
class btdiggs(object):
	url = 'http://btdigg.pw/'
	name = 'btdiggs'
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

		try:
			whatcode=''
			for i in range(20):
				try:
					locurl=urlgetlocation(self.url,data='keyword='+urllib.quote(what))
					if str(locurl.getcode())=='302':
						match = re.search("search\x2F(.*?)\x2F", locurl.geturl(), re.IGNORECASE | re.DOTALL)
						if match:
							whatcode = match.group(1)
						else:
							whatcode = ""
						xbmc.log(msg='btdiggs-err:%s  %s'%(int(locurl.getcode()),whatcode),level=xbmc.LOGERROR)
						break
				except Exception, errno:
					xbmc.log(msg='btdiggs-err:%s'%(errno),level=xbmc.LOGERROR)
					time.sleep(1)
					continue
			if whatcode=='':
				return result
			pageresult=''
			for i in range(10):
				searchurl=self.url+'search/%s/%s/%s/2.html'%(urllib.quote(whatcode),str(int(page)),str(sorttype),)
				pageresult = retrieve_url(searchurl,referer=self.url)
				if pageresult!='':
					break
				time.sleep(1)
				#xbmc.log(msg=pageresult,level=xbmc.LOGERROR)
			rmain=r'<dt><a.*?target=[\x22\x27]_blank[\x22\x27]>(?P<title>.*?)</a>.*?收录时间:<b>(?P<createtime>.*?)</b>.*?<span>文件大小:<b>(?P<filesize>.*?)</b>.*?<span>文件数:<b>(?P<filecount>.*?)</b>.*?<span>人气:<b>(?P<popular>.*?)</b>.*?href=[\x22\x27](?P<magnet>.*?)[\x22\x27]'
			reobj = re.compile(rmain, re.DOTALL)
			for match in reobj.finditer(pageresult):
				title=match.group('title')
				filesize=match.group('filesize')
				createtime=match.group('createtime')
				filecount=match.group('filecount')
				title = re.sub(r'<span\s+class="__cf_email.*?</span>', '', title, re.IGNORECASE | re.DOTALL)
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
			result['nextpage']=True
		except Exception, errno:
			xbmc.log(msg='btdiggs-err:%s'%(errno),level=xbmc.LOGERROR)
			return result
		
		result['state']=True
		return result