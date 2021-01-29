# -*- coding: utf-8 -*-
#VERSION: 1.00

from  __future__  import unicode_literals
import json,re
from commfunc import keyboard,_http,encode_obj
from six.moves.urllib import parse
from traceback import format_exc
from xbmcswift2 import Plugin
plugin=Plugin()
class ciligogo(object):
    url = 'http://www.ciligogo.info'
    name = 'ciligogo'
    support_sort=['relevance','addtime','size','popular'];
    page_result_count=10;
    supported_categories = {'all': ''}
    
    def __init__(self):
        pass
        
    def search(self, what, cat='all',sorttype='relevance',page='1'):
        result={}
        result['state']=False
        result['list']=[]
        result['sorttype']=sorttype
        
        if sorttype=='addtime': sorttype='time'
        elif sorttype=='size': sorttype='size'
        elif sorttype=='relevance': sorttype='rel'
        else : sorttype='hits'
        
        searchurl='%s/search/%s_%s_%s.html'%(self.url,parse.quote(what),str(sorttype),str(int(page)))
        #plugin.notify(searchurl)
        try:
            pageresult = _http(searchurl)
            
            #plugin.log.error(pageresult)
            rmain=r'\x2Fmagnet\x2F(?P<magnet>[a-z0-9]{40})\x2Ehtml.*?blank[\x22\x27]\x3E(?P<title>.*?)\x3C\x2Fa\x3E.*?创建时间.*?\x3Cb\x3E(?P<createtime>.*?)\x3C\x2Fb\x3E.*?文件大小.*?\x3E(?P<filesize>.*?)\x3C\x2Fb\x3E'
            reobj = re.compile(rmain, re.IGNORECASE | re.DOTALL)
            for match in reobj.finditer(pageresult):
                
                title=match.group('title').replace('<em>','').replace('</em>','')
                filesize=match.group('filesize')
                createtime=match.group('createtime')
                
                magnet=r'magnet:?xt=urn:btih:'+match.group('magnet')
                
                res_dict = dict()
                res_dict['name'] = title
                res_dict['size'] = filesize
                res_dict['filecount'] = ''
                res_dict['seeds'] = ''
                res_dict['leech'] = ''
                res_dict['link'] = magnet
                res_dict['date'] =createtime
                res_dict['desc_link'] = ''
                res_dict['engine_url'] = self.url
                result['list'].append(res_dict)
            if pageresult.find('&raquo;')>=0:
                result['nextpage']=True
        except Exception as ex:
            plugin.log.error(format_exc())
            return result
        
        result['state']=True
        return result