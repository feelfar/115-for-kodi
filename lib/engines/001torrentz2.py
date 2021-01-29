# -*- coding: utf-8 -*-
#VERSION: 1.00

from  __future__  import unicode_literals
import json,re
from commfunc import keyboard,_http,encode_obj
from six.moves.urllib import parse
from traceback import format_exc
from xbmcswift2 import Plugin
plugin=Plugin()
class torrentz2(object):
    url = 'https://torrentz2.torrentbay.to/'
    name = 'torrentz2'
    support_sort=['relevance','addtime','size','popular'];
    page_result_count=50;
    supported_categories = {'all': ''}
    
    def __init__(self):
        pass
        
    def search(self, what, cat='all',sorttype='relevance',page='1'):
        result={}
        result['state']=False
        result['list']=[]
        result['sorttype']=sorttype
        
        if sorttype=='addtime': sorttype='A'
        elif sorttype=='size': sorttype='S'
        elif sorttype=='relevance': sorttype='N'
        else : sorttype=''
        searchurl='%s/search%s?f=%s&p=%s'%(self.url,str(sorttype),parse.quote(what),str(int(page)-1))
        #plugin.notify(searchurl)
        try:
            pageresult = _http(searchurl)
            
            #plugin.log.error(pageresult)
            rmain=r'href\x3D\x2F(?P<magnet>[0-9a-f]{40})\x3E(?P<title>.*?)\x3C\x2Fa\x3E.*?span\s+title.*?\x3E(?P<createtime>.*?)\x3C\x2F.*?\x3Cspan\x3E(?P<filesize>.*?)\x3C\x2F'
            reobj = re.compile(rmain, re.IGNORECASE | re.DOTALL)
            for match in reobj.finditer(pageresult):
                
                title=match.group('title')
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
            if pageresult.find('>»</a>')>=0:
                result['nextpage']=True
        except Exception as ex:
            plugin.log.error(format_exc())
            return result
        
        result['state']=True
        return result