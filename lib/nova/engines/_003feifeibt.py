# -*- coding: utf-8 -*-
#VERSION: 1.00

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re,zlib,base64,HTMLParser
from xbmcswift2 import Plugin
plugin=Plugin()
class feifeibt(object):
	url = 'http://feifeibtba.net/search/'
	name = 'feifeibt'
	support_sort=['relevance','addtime','size','files','popular'];
	page_result_count=10;
	supported_categories = {'all': ''}

	def __init__(self):
		pass
		
	def search(self, what, cat='all',sorttype='relevance',page='1'): 
		result={}
		result['state']=False
		result['list']=[]
		result['sorttype']=sorttype
		#fuck,一个晚上才搞定
		what = base64.b64encode(zlib.compress(what)[2:-4])[0:-1]
		what = what.replace('/','_').replace('\x2B','-').replace('\x3D','')
		
		if sorttype=='addtime': sorttype='1'
		elif sorttype=='size': sorttype='2'
		elif sorttype=='files': sorttype='3'
		elif sorttype=='popular': sorttype='4'
		else : sorttype='0'
		
		
		'''
		if str(sorttype)=='-1':
			dialog = xbmcgui.Dialog()
			sorttype=dialog.select('btdb搜索-选择排序类型',['相关度','创建时间','文件大小','文件数','热度'])
			if sorttype==-1:
				return result
			sorttype=str(sorttype)
			'''
		
		searchurl=self.url+'%s/%s/%s/2.html'%(urllib.quote(what),str(int(page)),str(sorttype))

		try:
			pageresult = retrieve_url(searchurl)
			pageresult=HTMLParser().unescape(pageresult)
			plugin.log.error(pageresult)
			rmain=r'<dt>.*?_blank">(?P<title>.*?)</a>.*?href=\x27(?P<magnet>magnet.*?)\x27.*?<b>(?P<createtime>.*?)</b>.*?<b>(?P<filesize>.*?)</b>.*?<b>(?P<filecount>.*?)</b>.*?人气.*?<b>(?P<heatlevel>.*?)</b>'
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
			if pageresult.find('最后一页')>=0:
				result['nextpage']=True
		except:
			return result
		
		result['state']=True
		return result