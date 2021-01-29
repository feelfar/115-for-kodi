# -*- coding: utf-8 -*-
#VERSION: 1.00
from  __future__  import unicode_literals
import json,re
from commfunc import keyboard,_http,encode_obj
from six.moves.urllib import parse
from traceback import format_exc
from xbmcswift2 import Plugin
plugin=Plugin()
class bt2mag(object):
    url = 'https://tellme.pw/btsow'
    name = 'bt2mag'
    support_sort=[];
    page_result_count=30;
    supported_categories = {'all': ''}

    def __init__(self):
        pass

    def search(self, what, cat='all',sorttype='relevance',page='1'): 
    
        result={}
        result['state']=False
        result['list']=[]
        
        
        try:
            #searchurl='https://btsow.pw'
            pageresult = _http(self.url)
            match = re.search(r'<strong><a\x20href="(.*?)"', pageresult, re.DOTALL | re.MULTILINE)
            if match:
                searchurl = match.group(1)
            
            
            searchurl=searchurl+'/search/%s/page/%s'%(parse.quote(what),str(int(page)))

            pageresult = _http(searchurl)
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
            plugin.log.error(format_exc())
            return result
        
        result['state']=True
        return result
      