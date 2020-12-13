# -*- coding: utf-8 -*-
#VERSION: 1.30
#AUTHORS: BTDigg team (research@btdigg.org)

#                    GNU GENERAL PUBLIC LICENSE
#                       Version 3, 29 June 2007
#
#                   <http://www.gnu.org/licenses/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,re,xbmc,xbmcgui

from xbmcswift2 import Plugin
plugin=Plugin()
webproxy = plugin.get_storage('webproxy')

class btdigg(object):
	url = 'http://btdigg.org/search'
	name = 'btdigg'
	supported_categories = {'all': ''}

	
	def __init__(self):
		pass
		
	def download_torrent(self, info):
		print download_file(info, info)

	def getwebproxy(self):
		try:
			#plugin.notify('重新获取代理')
			pageresult = retrieve_url('http://www.fengherili.xyz/hao.php?server=0')
			
			match = re.search('action="(http://.*?)/', pageresult, re.DOTALL | re.MULTILINE)
			if match:
				return match.group(1)
			else:
				return ''
		except:
			return ''
	
	def search(self, what, cat='all',sorttype='-1',page='1'): 		
		result={}
		result['state']=False
		result['list']=[]
		
		if str(sorttype)=='-1':
			dialog = xbmcgui.Dialog()
			sorttype=dialog.select('btdigg搜索-选择排序类型',['相关度','下载热度','创建时间','文件大小','文件数'])
			if sorttype==-1:
				return result
			sorttype=str(sorttype)
		result['sorttype']=sorttype
		
		searchurl=self.url+'?q=%s&order=%s&p=%s'%(urllib.quote(what), sorttype,str(int(page)-1))		
		data = urllib.urlencode({'u': searchurl,'b':'12','f':'norefer'})
		pageresult=''
		for i in range(5):
			try:
				wp=webproxy.get('webproxy','')
				if not wp:
					#plugin.notify('重新获取代理')
					wp=self.getwebproxy()
					
				#plugin.notify('当前代理：'+webproxy['webproxy'])
				webproxyurl=wp+'/browse.php?'+data
				pageresult = retrieve_url(webproxyurl,referer=wp)
				if pageresult:
					webproxy['webproxy']=wp
					webproxy.sync()
					break
				else:
					continue
			except:
				continue
		if pageresult=='':
			webproxy['webproxy']=''
			webproxy.sync()
			return result
		try:
			rmain=r'"idx">.*?>(?P<title>[^<]+)</a>.*?href=".*?u=.*?(?P<magnet>magnet.*?)&.*?".*?attr_val">(?P<filesize>.*?)<.*?attr_val">(?P<filecount>.*?)<.*?attr_val">(?P<heatlevel>.*?)<.*?attr_val">(?P<createtime>.*?)<.*?attr_val">.*?attr_val">(?P<fake>.*?)<'
			reobj = re.compile(rmain, re.DOTALL | re.MULTILINE)
			#xbmc.log(msg=pageresult)
			for match in reobj.finditer(pageresult):
				fake=match.group('fake')
				if fake=='No' or fake=='否':
					title=match.group('title')
					filesize=match.group('filesize').replace('&nbsp;',' ')
					createtime=match.group('createtime').replace('&nbsp;',' ')
					filecount=match.group('filecount')
					magnet=match.group('magnet')
				else:
					magnet=''		
					continue
				res_dict = dict()
				res_dict['name'] = title
				res_dict['size'] = filesize
				res_dict['seeds'] = match.group('heatlevel')
				res_dict['leech'] = match.group('heatlevel')
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
	  