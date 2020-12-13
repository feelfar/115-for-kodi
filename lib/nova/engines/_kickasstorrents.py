# -*- coding: utf-8 -*-
#VERSION: 1.28
#AUTHORS: Christophe Dumez (chris@qbittorrent.org)
#CONTRIBUTORS: Diego de las Heras (diegodelasheras@gmail.com)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import json,urllib,xbmcgui

class kickasstorrents(object):
	url = 'https://kickass.sx/'
	name = 'Kickass Torrents'
	supported_categories = {'all': '', 'movies': 'Movies', 'tv': 'TV', 'music': 'Music', 'games': 'Games', 'software': 'Applications'}

	def __init__(self):
		pass

	def download_torrent(self, info):
		print download_file(info, info)

	def search(self, what, cat='all',sorttype='-1',page=1):
		result={}
		result['state']=False
		result['list']=[]
		
		if str(sorttype)=='-1':
			dialog = xbmcgui.Dialog()
			sorttype=dialog.select('Kickass搜索-选择排序类型',['种子数','下载热度','文件大小','创建时间','文件数'])
			if sorttype==-1:
				return result
				
		sorttype=str(sorttype)
		if sorttype=='2': sorttype='size'
		elif sorttype=='4': sorttype='files_count'
		elif sorttype=='3': sorttype='time_add'
		elif sorttype=='1': sorttype='leechers'
		elif sorttype=='0': sorttype='seeders'	
		result['sorttype']=sorttype
		
		json_data = retrieve_url(self.url+'/json.php?q=%s&field=%s&sorder=desc&page=%s'%(urllib.quote(what), sorttype,str(page)))
		
		try:
			json_dict = json.loads(json_data)
		except:
			return result
		if int(json_dict['total_results']) <= 0:
			return result
		else:
			result['nextpage']=json_dict['total_results']>int(page)*25
		
		for r in json_dict['list']:
			try:
				if cat != 'all' and self.supported_categories[cat] != r['category']:
					continue
				res_dict = dict()
				res_dict['name'] = r['title']				
				res_dict['size'] = str(r['size'])
				res_dict['seeds'] = r['seeds']
				res_dict['leech'] = r['leechs']
				res_dict['link'] ='magnet:?xt=urn:btih:'+ r['hash']
				res_dict['date'] = r['pubDate']
				res_dict['desc_link'] = r['link'].replace('http://', 'https://')
				res_dict['engine_url'] = self.url
				result['list'].append(res_dict)
			except:
				return result
		result['state']=True
		return result
	  